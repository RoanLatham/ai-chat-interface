import os
from datetime import datetime
import logging
import re
from typing import List
from flask import Flask, Response, request, jsonify, send_from_directory
from llama_cpp import Llama
from Conversation import Conversation, create_conversation, save_conversation, load_conversation, load_all_conversations, Node
import json
import time


# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='app.log',
                    filemode='a')

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Directory containing AI models
MODELS_DIR = "ai_models"
# Directory containing AI conversations
CONVERSATIONS_DIR = ".\conversations"

current_model = None 
current_model_name = None

current_conversation = None

NAMING_PROMPT = """Based on the user's first message, generate a short, concise title for this conversation. The title should be no more than 5 words long and should capture the essence of the topic or query. if the message is vague or doesn't describe a definitive topic, try to include words form the users message in the title, if that still doesn't work, use a more general title. Respond with only the title, nothing else."""

def load_system_prompt():
    with open('system-prompt.txt', 'r') as file:
        return file.read().strip()

SUPER_SYSTEM_PROMPT = load_system_prompt()

DEFAULT_SYSTEM_PROMPT = """ """

current_system_prompt = DEFAULT_SYSTEM_PROMPT

CONVERSATION_INSTRUCTIONS_START = "The following are conversation-specific instructions provided by the user for this interaction:"

CONVERSATION_HISTORY_START = """End of conversation-specific instructions.

The conversation history begins below. Focus on the latest human response and continue the conversation accordingly:"""

STOP_PHRASES = ["Human:",
                "End of example interactions",
                "Now ending this interaction",
                "[INST]",
                "[Assistant",
                "End of internal thought",
                "Please respond as the AI",
                "end of interaction.",
                "<|eot_id|>",
                "<|end_of_text|>",
                "<>",
                "<</SYS>>",
                "<user>",
                "</user>",
                "<<user>>",
                "<</user>>",
                "</AI Response>",
                "<</AI Response>>",
                "</AI Internal Thought>",
                "<</AI Internal Thought>>",
                "Your response is awaited."]

INTERNAL_THOUGHT_PROMPT = """
Analyze the conversation history and the user's latest message. Formulate a strategy for responding, considering:
1. Key points to address
2. Tone and style appropriate for the context
3. Potential clarifications or additional information needed
4. Any relevant background knowledge to incorporate
5. the best way to format the response using codeblocks headings, list, numbered lists etc, if necessary

Format your thoughts clearly and concisely. This is for internal planning only and will not be shown to the user.

you will be provided with an opening <AI Internal Thought> tag, you must end your response with a closing response tag: </AI Internal Thought>
"""


def generate_ai_response(conversation: Conversation, model_name: str, max_tokens: int = 300): #-> Generator[str, None, None]:
    global current_model, current_model_name

    if current_model is None or current_model_name != model_name:
        yield json.dumps({"status": "loading_model"})
        current_model = load_model(model_name)
        current_model_name = model_name

    yield json.dumps({"status": "generating"})

    try:
        # Prepare conversation history with GAtt formatting and limit to max_tokens
        history = prepare_gatt_history(conversation, max_tokens=max_tokens)
        
        # Generate internal thought
        internal_thought = generate_internal_thought(current_model, history)
        
        # Generate AI response
        ai_response = generate_final_response(current_model, history, internal_thought)
        
        # Add the new message to the conversation
        ai_node = conversation.add_message(ai_response, "AI", current_model_name, internal_thought)
        save_conversation(conversation, CONVERSATIONS_DIR)
        
        yield json.dumps({
            "status": "complete",
            "response": ai_response,
            "node_id": ai_node.id,
            "timestamp": ai_node.timestamp.isoformat()
        })
    except ValueError as e:
        if "exceed context window" in str(e):
            # Attempt to reduce context and retry once
            reduced_history = reduce_context(conversation, e, max_tokens)
            try:
                internal_thought = generate_internal_thought(current_model, reduced_history)
                ai_response = generate_final_response(current_model, reduced_history, internal_thought)
                ai_node = conversation.add_message(ai_response, "AI", current_model_name, internal_thought)
                save_conversation(conversation, CONVERSATIONS_DIR)
                yield json.dumps({
                    "status": "complete",
                    "response": ai_response,
                    "node_id": ai_node.id,
                    "timestamp": ai_node.timestamp.isoformat()
                })
            except Exception:
                yield json.dumps({"status": "error", "message": "Context too large even after reduction"})
        else:
            yield json.dumps({"status": "error", "message": str(e)})

def prepare_gatt_history(conversation: Conversation, max_tokens: int = 300) -> str:
    start_time = time.time()

    def format_node(node: Node) -> str:
        if node.sender == "Human":
            return f"<user>{node.content}</user>\n"
        else:
            internal_thought = f"<AI Internal Thought>{node.internal_monologue}</AI Internal Thought>\n" if node.internal_monologue else ""
            return f"{internal_thought}<AI Response>{node.content}</AI Response>\n\n"

    def tokenize(text: str) -> List[int]:
        return current_model.tokenize(text.encode('utf-8'))

    def count_tokens(text: str) -> int:
        return len(tokenize(text))

    branch = conversation.get_current_branch()
    
    # Ensure we have at least 3 message groups or all available if less
    guaranteed_nodes = branch[-min(6, len(branch)):]
    remaining_nodes = branch[:-len(guaranteed_nodes)]

    # Format and tokenize guaranteed messages
    guaranteed_history = "\n".join(format_node(node) for node in guaranteed_nodes)
    guaranteed_tokens = count_tokens(guaranteed_history)

    # Prepare the rest of the history
    remaining_history = []
    current_tokens = guaranteed_tokens
    omission_notice = "<system>Some messages have been omitted to fit the context window.</system>"
    omission_tokens = count_tokens(omission_notice)

    for node in reversed(remaining_nodes):
        formatted_node = format_node(node)
        node_tokens = count_tokens(formatted_node)
        
        if current_tokens + node_tokens + omission_tokens <= max_tokens:
            remaining_history.insert(0, formatted_node)
            current_tokens += node_tokens
        else:
            remaining_history.insert(0, omission_notice)
            current_tokens += omission_tokens
            break

    # Combine the parts
    final_history = f"{guaranteed_history}\n" + "\n".join(remaining_history)

    end_time = time.time()
    execution_time = end_time - start_time
    logging.info(f"Prepared conversation history with ~{current_tokens} tokens in {execution_time:.4f} seconds")
    logging.info(f"History length: {len(branch)} messages, {len(remaining_nodes)} potentially trimmed")
    return final_history

def generate_internal_thought(model, history):
    prompt = f"{SUPER_SYSTEM_PROMPT}\n\n{history}\n\n{INTERNAL_THOUGHT_PROMPT}\n<AI Internal Thought>"
    response = model(prompt, max_tokens=500, stop=STOP_PHRASES)
    return response['choices'][0]['text'].strip()

def generate_final_response(model, history, internal_thought):
    prompt = f"{SUPER_SYSTEM_PROMPT}\n\n{history}\n\n<AI Internal Thought>{internal_thought}\n\n<AI Response>"
    response = model(prompt, max_tokens=4096, stop=STOP_PHRASES)
    return response['choices'][0]['text'].strip()

def reduce_context(conversation: Conversation, error: ValueError, max_tokens: int) -> str:
    tokens_to_reduce = int(re.search(r'\((\d+)\)', str(error)).group(1))
    buffer = int(tokens_to_reduce * 1.5)  # Add 50% buffer
    
    reduced_max_tokens = max(max_tokens - buffer, 500)  # Ensure we don't go below a minimum threshold
    return prepare_gatt_history(conversation, max_tokens=reduced_max_tokens)


def load_model(model_name):
    global current_model, current_model_name
    if current_model_name != model_name:
        selected_model_path = os.path.join(MODELS_DIR, model_name)
        # Convert backslashes to forward slashes and ensure it starts with "./"
        selected_model_path = "./" + selected_model_path.replace("\\", "/")
        logging.info(f"Loading model: {selected_model_path}")
        current_model = Llama(model_path=selected_model_path, n_ctx=4096, n_threads=8, seed=42, f16_kv=True, use_mlock=True)
        current_model_name = model_name
    return current_model

def get_available_models():
    return [f for f in os.listdir(MODELS_DIR) if f.endswith('.gguf')]

@app.route('/')
def index():
    return send_from_directory('.', 'chat-interface.html')

@app.route('/models')
def models():
    available_models = get_available_models()
    if not available_models:
        return jsonify({"error": "No AI models found in the ai_models folder."}), 404
    return jsonify({
        "models": available_models,
        "current_model": current_model_name
    })


@app.route('/conversations', methods=['GET'])
def get_conversations():
    conversations = load_all_conversations(CONVERSATIONS_DIR)
    return jsonify([
        {
            'id': conv.id,
            'name': conv.name,
            'timestamp': conv.latest_message_timestamp.isoformat() if conv.latest_message_timestamp else None
        }
        for conv in conversations
    ])

@app.route('/conversation/switch', methods=['POST'])
def switch_conversation():
    global current_conversation
    conversation_id = request.json['id']
    if current_conversation:
        save_conversation(current_conversation, CONVERSATIONS_DIR)
    current_conversation = load_conversation(conversation_id, CONVERSATIONS_DIR)
    return jsonify({
        'success': True,
        'conversation_id': current_conversation.id,
        'conversation_name': current_conversation.name,
        'branch': [
            {
                'id': node.id,
                'content': node.content,
                'sender': node.sender,
                'timestamp': node.timestamp.isoformat(),
                'model_name': node.model_name
            } for node in current_conversation.get_current_branch()
        ]
    })

@app.route('/conversation/delete', methods=['POST'])
def delete_conversation():
    global current_conversation
    conversation_id = request.json['id']
    filename = os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.pickle")
    
    try:
        if os.path.exists(filename):
            os.remove(filename)
            if current_conversation and current_conversation.id == conversation_id:
                current_conversation = None
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Conversation file not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to delete conversation: {str(e)}'}), 500

@app.route('/conversation/clear', methods=['POST'])
def clear_conversation():
    global current_conversation
    if current_conversation:
        save_conversation(current_conversation, CONVERSATIONS_DIR)
    current_conversation = None
    return jsonify({'success': True})

@app.route('/rename_conversation', methods=['POST'])
def rename_conversation():
    data = request.json
    conversation_id = data['conversation_id']
    new_name = data['new_name']
    
    try:
        conversation = load_conversation(conversation_id, CONVERSATIONS_DIR)
        conversation.set_name(new_name)
        save_conversation(conversation, CONVERSATIONS_DIR)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/current_conversation', methods=['GET'])
def get_current_conversation():
    if current_conversation:
        return jsonify({
            'conversation_id': current_conversation.id,
            'conversation_name': current_conversation.name,
            'branch': [
                {
                    'id': node.id,
                    'content': node.content,
                    'sender': node.sender,
                    'timestamp': node.timestamp.isoformat(),
                    'model_name': node.model_name
                } for node in current_conversation.get_current_branch()
            ]
        })
    else:
        return jsonify({'conversation_id': None, 'conversation_name': None, 'branch': []})

@app.route('/switch_branch', methods=['POST'])
def switch_branch():
    data = request.json
    node_id = data['node_id']
    direction = data['direction']
    
    if current_conversation:
        siblings = current_conversation.get_siblings(node_id)
        current_index = next((i for i, sibling in enumerate(siblings) if sibling.id == node_id), -1)
        
        if direction == 'left' and current_index > 0:
            new_node = siblings[current_index - 1]
        elif direction == 'right' and current_index < len(siblings) - 1:
            new_node = siblings[current_index + 1]
        else:
            return jsonify({'success': False, 'error': 'Cannot switch branch in this direction'}), 400
        
        leaf_node = current_conversation.tree.get_leaf_node(new_node)
        current_conversation.tree.current_node = leaf_node
        save_conversation(current_conversation, CONVERSATIONS_DIR)
        
        return jsonify({
            'success': True,
            'conversation_id': current_conversation.id,
            'branch': [
                {
                    'id': node.id,
                    'content': node.content,
                    'sender': node.sender,
                    'timestamp': node.timestamp.isoformat(),
                    'model_name': node.model_name
                } for node in current_conversation.get_current_branch()
            ]
        })
    
    return jsonify({'success': False, 'error': 'No active conversation'}), 400

@app.route('/add_user_message', methods=['POST'])
def add_user_message():
    global current_system_prompt, current_model, current_conversation, current_model_name
    data = request.json
    user_input = data['message']
    model_name = data['model']
    if 'system_prompt' in data:
        current_system_prompt = data['system_prompt']
    
    def generate(user_input, model_name):
        global current_model, current_conversation, current_model_name
        
        if current_model is None or current_model_name != model_name:
            yield json.dumps({"status": "loading_model"})
            print(f"Loading model: {model_name}")
            current_model = load_model(model_name)
            current_model_name = model_name
        
        if current_conversation is None:
            yield json.dumps({"status": "creating_conversation"})
            print("Creating new conversation")
            naming_prompt = f"{NAMING_PROMPT}\n\nUser's message: {user_input}\n\nTitle:"
            naming_response = current_model(naming_prompt, max_tokens=10, stop=["\n"], temperature=0.7)
            conversation_name = naming_response['choices'][0]['text'].strip()
            current_conversation = create_conversation(conversation_name)
            
        
        new_node = current_conversation.add_message(user_input, "Human")
        save_conversation(current_conversation, CONVERSATIONS_DIR)
        
        yield json.dumps({
            "status": "complete",
            "conversation_id": current_conversation.id,
            "conversation_name": current_conversation.name,
            "human_node_id": new_node.id,
            "timestamp": new_node.timestamp.isoformat()
        })
    
    return Response(generate(user_input, model_name), mimetype='application/json')

@app.route('/get_ai_response', methods=['POST'])
def get_ai_response():
    global current_conversation
    data = request.json
    conversation_id = data['conversation_id']
    model_name = data['model']
    
    if current_conversation.id != conversation_id:
        current_conversation = load_conversation(conversation_id, CONVERSATIONS_DIR)
    
    return Response(generate_ai_response(current_conversation, model_name), mimetype='application/json')

@app.route('/regenerate_response', methods=['POST'])
def regenerate_response():
    data = request.json
    node_id = data['node_id']
    model_name = data['model']
    
    if current_conversation:
        node_to_regenerate = current_conversation.find_node(node_id)
        if node_to_regenerate and node_to_regenerate.parent:
            current_conversation.tree.current_node = node_to_regenerate.parent
            return Response(generate_ai_response(current_conversation, model_name), mimetype='application/json')
    
    return jsonify({'success': False, 'error': 'Failed to regenerate response'}), 400

@app.route('/edit_message', methods=['POST'])
def edit_message():
    data = request.json
    node_id = data['node_id']
    new_content = data['new_content']
    sender = data['sender']
    
    if current_conversation:
        new_node = current_conversation.edit_message(node_id, new_content)
        if new_node:
            save_conversation(current_conversation, CONVERSATIONS_DIR)
            
            return jsonify({
                'success': True,
                'new_node_id': new_node.id,
                'timestamp': new_node.timestamp.isoformat(),
            })
    
    return jsonify({'success': False, 'error': 'Failed to edit message'}), 400

@app.route('/get_original_content', methods=['POST'])
def get_original_content():
    data = request.json
    node_id = data['node_id']
    logging.info(f"Getting original content for node_id: {node_id}")
    
    if current_conversation:
        node = current_conversation.find_node(node_id)
        if node:
            return jsonify({
                'success': True,
                'content': node.content
            })
    
    return jsonify({'success': False, 'error': 'Node not found'}), 404

@app.route('/get_siblings', methods=['POST'])
def get_siblings():
    data = request.json
    node_id = data['node_id']
    
    if current_conversation:
        siblings = current_conversation.get_siblings(node_id)
        return jsonify({
            'siblings': [
                {
                    'id': node.id,
                    'content': node.content,
                    'sender': node.sender,
                    'timestamp': node.timestamp.isoformat(),
                    'model_name': node.model_name
                } for node in siblings
            ]
        })
    
    return jsonify({'siblings': []}), 400

@app.route('/system_prompt', methods=['GET'])
def get_system_prompt():
    return jsonify({'system_prompt': current_system_prompt})

@app.route('/default_system_prompt', methods=['GET'])
def get_default_system_prompt():
    return jsonify({'default_system_prompt': DEFAULT_SYSTEM_PROMPT})

@app.route('/models_folder_path', methods=['GET'])
def get_models_folder_path():
    return jsonify({'path': os.path.abspath(MODELS_DIR)})

@app.route('/open_models_folder', methods=['POST'])
def open_models_folder():
    import subprocess
    try:
        if os.name == 'nt':  # Windows
            os.startfile(MODELS_DIR)
        elif os.name == 'posix':  # macOS and Linux
            subprocess.call(['open', MODELS_DIR])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(CONVERSATIONS_DIR, exist_ok=True)
    app.run(debug=True)
