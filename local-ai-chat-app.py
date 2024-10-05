import os
from datetime import datetime
import logging
from flask import Flask, request, jsonify, send_from_directory
from llama_cpp import Llama
from Conversation import Conversation, create_conversation, save_conversation, load_conversation, load_all_conversations

# Dev randomly name conversations with UUID for now
import uuid

app = Flask(__name__)

# Directory containing AI models
MODELS_DIR = "ai_models"
# Directory containing AI conversations
CONVERSATIONS_DIR = ".\conversations"

current_model = None 
current_model_name = None

current_conversation = None

NAMING_PROMPT = """Based on the user's first message, generate a short, concise title for this conversation. The title should be no more than 5 words long and should capture the essence of the topic or query. Respond with only the title, nothing else."""

def load_system_prompt():
    with open('system-prompt.txt', 'r') as file:
        return file.read().strip()

SUPER_SYSTEM_PROMPT = load_system_prompt()





DEFAULT_SYSTEM_PROMPT = """You are a helpful, respectful, and honest AI assistant. Always provide accurate information and if you're unsure, admit it. Prioritize user safety and well-being in your responses. Be concise yet informative, and tailor your language to the user's level of understanding. Respect privacy and ethical boundaries in your interactions."""

current_system_prompt = DEFAULT_SYSTEM_PROMPT

def load_model(model_name):
    global current_model, current_model_name
    if current_model_name != model_name:
        selected_model_path = os.path.join(MODELS_DIR, model_name)
        # Convert backslashes to forward slashes and ensure it starts with "./"
        selected_model_path = "./" + selected_model_path.replace("\\", "/")
        logging.info(f"Loading model: {selected_model_path}")
        current_model = Llama(model_path=selected_model_path, n_ctx=8192, n_threads=8, seed=42, f16_kv=True, use_mlock=True)
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
    return jsonify(available_models)

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


def generate_ai_response(conversation: Conversation):
    conversation_history = "\n".join([f"{node.sender}: {node.content}\nAI Internal Thought Process: {node.internal_monologue}" for node in conversation.get_current_branch()])
    full_prompt = f"{SUPER_SYSTEM_PROMPT}\n\nsystem prompt: {current_system_prompt}\n\n{conversation_history}\nAI Internal Thought Process:"
    
    response = current_model(full_prompt, max_tokens=10000, stop=["Human:"], temperature=0.7, top_p=0.9, top_k=40, repeat_penalty=1.1, presence_penalty=0.1, frequency_penalty=0.01, mirostat_mode=2, mirostat_tau=5.0, mirostat_eta=0.1, echo=True)
    ai_full_response = response['choices'][0]['text'].split("AI Internal Thought Process:")[-1].strip()
    
    # Split the response into internal monologue and actual response
    parts = ai_full_response.split("AI:", 1)
    internal_monologue = parts[0].strip() if len(parts) > 1 else ""
    ai_response = parts[1].strip() if len(parts) > 1 else ai_full_response.strip()
    
    ai_node = conversation.add_message(ai_response, "AI", current_model_name, internal_monologue)

    print(f"full AI Response: {internal_monologue + ai_response}")
    save_conversation(conversation, CONVERSATIONS_DIR)
    
    return ai_response, ai_node

@app.route('/chat', methods=['POST'])
def chat():
    global current_system_prompt, current_model, current_conversation, current_model_name
    data = request.json
    user_input = data['message']
    model_name = data['model']
    if 'system_prompt' in data:
        current_system_prompt = data['system_prompt']
    
    if current_model is None or current_model_name != model_name:
        current_model = load_model(model_name)
    
    if current_conversation is None:
        naming_prompt = f"{NAMING_PROMPT}\n\nUser's message: {user_input}\n\nTitle:"
        naming_response = current_model(naming_prompt, max_tokens=10, stop=["\n"], temperature=0.7)
        conversation_name = naming_response['choices'][0]['text'].strip()
        current_conversation = create_conversation(conversation_name)
        logging.info("new conversation created with id: ", current_conversation.id)
    
    new_node = current_conversation.add_message(user_input, "Human")
    
    ai_response, ai_node = generate_ai_response(current_conversation)
    
    return jsonify({
        'response': ai_response,
        'conversation_id': current_conversation.id,
        'conversation_name': current_conversation.name,
        'model_name': current_model_name,
        'human_node_id': new_node.id,
        'ai_node_id': ai_node.id,
        'timestamp': ai_node.timestamp.isoformat()
    })

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
            
            if sender.lower() == 'human':
                # Generate new AI response for edited human message
                ai_response, ai_node = generate_ai_response(current_conversation)
            else:
                # No need to generate response for AI message edit
                ai_response, ai_node = None, None
            
            return jsonify({
                'success': True,
                'new_node_id': new_node.id,
                'timestamp': new_node.timestamp.isoformat(),
                'ai_response': ai_response,
                'ai_node_id': ai_node.id if ai_node else None,
                'ai_timestamp': ai_node.timestamp.isoformat() if ai_node else None
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

if __name__ == '__main__':
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(CONVERSATIONS_DIR, exist_ok=True)
    app.run(debug=True)
