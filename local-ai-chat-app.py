import os
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import re
import sys
import platform
from typing import List
from flask import Flask, Response, request, jsonify, send_from_directory
from llama_cpp import Llama
from conversation import Conversation, create_conversation, save_conversation, load_conversation, load_all_conversations, Node, CONVERSATION_VERSION
import json
import time
import subprocess
import webbrowser
import threading
from dataclasses import dataclass

# Determine if running in packaged mode or development mode
def is_packaged():
    """Check if the application is running as a packaged executable"""
    return getattr(sys, 'frozen', False)

# Get the base directory for the application
def get_base_dir():
    """Get the base directory for the application (different in dev vs packaged)"""
    if is_packaged():
        # When packaged with PyInstaller, sys._MEIPASS contains the path to the bundle
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        # For other packagers, use the executable's directory
        return os.path.dirname(sys.executable)
    else:
        # In development mode, use the script directory
        return os.path.dirname(os.path.abspath(__file__))

# Get user data directory (for models, conversations)
def get_user_data_dir():
    """Get the directory for user data that should persist across app updates"""
    if is_packaged():
        # In packaged mode, store user data next to the executable
        return os.path.dirname(sys.executable)
    else:
        # In development mode, use the current directory
        return os.path.dirname(os.path.abspath(__file__))

# Initialize paths
BASE_DIR = get_base_dir()
USER_DATA_DIR = get_user_data_dir()

# Configure custom logging
def setup_logging():
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(USER_DATA_DIR, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    app_logger = logging.getLogger('app')
    app_logger.setLevel(logging.INFO)
    
    # File handler - write to user data directory
    log_file = os.path.join(logs_dir, 'app.log')
    file_handler = RotatingFileHandler(log_file, maxBytes=10000000, backupCount=5)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    app_logger.addHandler(file_handler)
    
    # Console handler for app_logger
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    app_logger.addHandler(console_handler)
    
    # Configure Flask logging
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.INFO)
    werkzeug_logger.addHandler(console_handler)
    
    # Remove default handlers from the root logger
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    return app_logger

app_logger = setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Disable Flask's default logging
app.logger.handlers = []
app.logger.propagate = False

# Directory containing AI models
MODELS_DIR = os.path.join(USER_DATA_DIR, "ai_models")
# Directory containing AI conversations
CONVERSATIONS_DIR = os.path.join(USER_DATA_DIR, "conversations")
# System prompt file location
SYSTEM_PROMPT_PATH = os.path.join(BASE_DIR, "system-prompt.txt")

# Initialize directories
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)

current_model = None 
current_model_name = None

current_conversation = None

NAMING_PROMPT = """Based on the user's first message, generate a short, concise title for this conversation. The title should be no more than 5 words long and should capture the essence of the topic or query. if the message is vague or doesn't describe a definitive topic, try to include words form the users message in the title, if that still doesn't work, use a more general title. Respond with only the title, nothing else."""

# Load system prompt from file
def load_session_prompt():
    try:
        with open(SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        app_logger.warning("System prompt file not found, using default session prompt")
        return DEFAULT_SESSION_PROMPT

SYSTEM_PROMPT = load_session_prompt()

DEFAULT_SESSION_PROMPT = """You are a helpful AI assistant. You are knowledgeable, friendly, and always strive to provide accurate and useful information."""

current_session_prompt = DEFAULT_SESSION_PROMPT

SESSION_PROMPT_PREPEND ="""The following are conversation-specific instructions provided by the user for this interaction: 
<<SYS>>"""

SESSION_PROMPT_APPEND = """<</SYS>>
End of conversation-specific instructions.

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
                "<AI Response>",
                "</AI Response>",
                "<</AI Response>>",
                "<AI Internal Thought>",
                "</AI Internal Thought>",
                "<</AI Internal Thought>>",
                "Your response is awaited."]

internal_monologue_PROMPT = """
Analyze the conversation history and the user's latest message. Formulate a strategy for responding, considering:
1. Key points to address
2. Tone and style appropriate for the context
3. Potential clarifications or additional information needed
4. Any relevant background knowledge to incorporate
5. the best way to format the response using codeblocks headings, list, numbered lists etc, if necessary

Format your planning thoughts clearly and concisely. This is for internal planning only and will not be shown to the user.

you will be provided with an opening <AI Internal Thought> tag, you must end your response with a closing response tag: </AI Internal Thought>
"""

@dataclass
class TokenLimits:
    max_tokens: int
    target_tokens: int = None

    def __post_init__(self):
        if self.target_tokens is None:
            # Set target to 95% of max by default
            self.target_tokens = int(self.max_tokens * 0.95)
        
        if self.target_tokens > self.max_tokens:
            raise ValueError("Target tokens cannot exceed max tokens")

# Generate AI response for a given conversation, user message must already be added to conversation
def generate_ai_response(conversation: Conversation, model_name: str, planning_mode: bool = False, token_limits: TokenLimits = TokenLimits(4096)): #-> Generator[str, None, None]:
    start_time = time.time()
    global current_model, current_model_name

    if current_model is None or current_model_name != model_name:
        yield json.dumps({"status": "loading_model"})
        model_load_start = time.time()
        current_model = load_model(model_name)
        current_model_name = model_name
        app_logger.info(f"Model loading took {time.time() - model_load_start:.4f} seconds")

    yield json.dumps({"status": "generating"})

    try:
        # Store the internal planning for inclusion in the final response
        internal_monologue = None
        
        # Generate internal planning only if planning mode is enabled
        if planning_mode:
            planning_start = time.time()
            internal_monologue = generate_internal_monologue(current_model, conversation, token_limits)
            planning_time = time.time() - planning_start
            app_logger.info(f"Internal planning generation took {planning_time:.4f} seconds")
            
            # Show the internal planning as a separate message
            planning_message = internal_monologue
            yield json.dumps({
                "status": "planning",
                "planning": planning_message,
                "timestamp": datetime.now().isoformat()
            })
        else:
            # Use placeholder internal planning when planning mode is disabled
            internal_monologue = "planning mode is disabled. Proceeding directly to response."
            app_logger.info("planning mode disabled, skipping planning generation")
        
        # Generate AI response
        response_start = time.time()
        ai_response = generate_final_response(current_model, conversation, internal_monologue, token_limits)
        response_time = time.time() - response_start
        app_logger.info(f"Final response generation took {response_time:.4f} seconds")

        # Add the new message to the conversation
        save_start = time.time()
        # Only save the internal planning in the node if planning mode was enabled
        saved_internal_monologue = internal_monologue if planning_mode else None
        ai_node = conversation.add_message(ai_response, "AI", current_model_name, saved_internal_monologue)
        save_conversation(conversation, CONVERSATIONS_DIR)
        save_time = time.time() - save_start
        app_logger.info(f"Saving conversation took {save_time:.4f} seconds")
        
        total_time = time.time() - start_time
        app_logger.info(f"Total AI response generation took {total_time:.4f} seconds")
        
        yield json.dumps({
            "status": "complete",
            "response": ai_response,
            "node_id": ai_node.id,
            "timestamp": ai_node.timestamp.isoformat(),
            "planning": internal_monologue if planning_mode else None
        })
    except ValueError as e:
        app_logger.warning(f"{str(e)}")
        yield json.dumps({"status": "error", "message": str(e)})

def tokenize(text: str) -> List[int]:
    return current_model.tokenize(text.encode('utf-8'))

def count_tokens(text: str) -> int:
    return len(tokenize(text))

# Prepare conversation history in GAtt format
def prepare_gatt_history(conversation: Conversation, token_limits: TokenLimits) -> str:
    start_time = time.time()

    def format_node(node: Node) -> str:
        if node.sender == "Human":
            return f"<user>{node.content}</user>\n"
        else:
            internal_monologue = f"<AI Internal Thought>{node.internal_monologue}</AI Internal Thought>\n" if node.internal_monologue else ""
            return f"{internal_monologue}<AI Response>{node.content}</AI Response>\n\n"

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
    target_tokens_remaining = token_limits.target_tokens - current_tokens
    omission_notice = "<s>Some messages have been omitted to fit the context window.</s>"
    omission_tokens = count_tokens(omission_notice)

    for node in reversed(remaining_nodes):
        formatted_node = format_node(node)
        node_tokens = count_tokens(formatted_node)
        
        if current_tokens + node_tokens + omission_tokens <= target_tokens_remaining:
            remaining_history.insert(0, formatted_node)
            current_tokens += node_tokens
        else:
            remaining_history.insert(0, omission_notice)
            current_tokens += omission_tokens
            break

    # Combine the parts
    final_history = f"{guaranteed_history}\n" + "\n".join(remaining_history)

    # Final check against max_tokens
    final_tokens = count_tokens(final_history)
    if final_tokens > token_limits.max_tokens:
        raise ValueError(f"Failed to reduce context: Final context ({final_tokens} tokens) exceeds maximum allowed ({token_limits.max_tokens} tokens)")

    end_time = time.time()
    execution_time = end_time - start_time
    app_logger.info(f"Prepared conversation history with ~{current_tokens} tokens in {execution_time:.4f} seconds")
    app_logger.info(f"History length: {len(branch)} messages, {len(remaining_nodes)} potentially trimmed")
    app_logger.info(f"Final history: {final_history}")
    return final_history

# Prepare full prompt including system prompts and conversation history
def prepare_full_prompt(history: str, token_limits: TokenLimits, internal_monologue: str = "") -> str:
    full_prompt = f"{SYSTEM_PROMPT}\n\n"
    
    if current_session_prompt:
        full_prompt += f"{SESSION_PROMPT_PREPEND}\n{current_session_prompt}\n{SESSION_PROMPT_APPEND}\n\n"
    
    full_prompt += f"{history}\n\n"
    
    if internal_monologue:
        full_prompt += f"<AI Internal Thought>{internal_monologue}</AI Internal Thought>\n\n"

    # Final check against max_tokens
    final_tokens = count_tokens(full_prompt)
    if final_tokens > token_limits.max_tokens:
        raise ValueError(f"Failed to reduce context: Final context ({final_tokens} tokens) exceeds maximum allowed ({token_limits.max_tokens} tokens)")
    
    app_logger.info(f"Prepared full prompt: \n{full_prompt}")

    return full_prompt

# Generate internal planning for AI response
def generate_internal_monologue(model, conversation, token_limits: TokenLimits):
    history_start = time.time()
    history = prepare_gatt_history(conversation, token_limits)
    prompt = prepare_full_prompt(history, token_limits=token_limits) + f"\n\n{internal_monologue_PROMPT}\n<AI Internal Thought>"
    app_logger.info(f"Internal Planning prompt preparation took {time.time() - history_start:.4f} seconds")
    
    inference_start = time.time()
    response = model(prompt, max_tokens=500, stop=STOP_PHRASES)
    stripped_response = response['choices'][0]['text'].strip()
    app_logger.info(f"<AI Internal Thought>\n{stripped_response}\n</AI Internal Thought>")
    app_logger.info(f"Internal Planning inference took {time.time() - inference_start:.4f} seconds")
    return stripped_response

# Generate final AI response
def generate_final_response(model, conversation, internal_monologue: str, token_limits: TokenLimits):
    history_start = time.time()
    history = prepare_gatt_history(conversation, token_limits)
    prompt = prepare_full_prompt(history, token_limits, internal_monologue) + "<AI Response>"
    app_logger.info(f"Final response prompt preparation took {time.time() - history_start:.4f} seconds")
    
    inference_start = time.time()
    response = model(prompt, max_tokens=4096, stop=STOP_PHRASES)
    stripped_response = response['choices'][0]['text'].strip()
    app_logger.info(f"<AI Response>\n{stripped_response}\n</AI Response>")
    app_logger.info(f"Final response inference took {time.time() - inference_start:.4f} seconds")
    return stripped_response

# Load AI model
def load_model(model_name):
    global current_model, current_model_name
    if current_model_name != model_name:
        if not hasattr(load_model, 'model_cache'):
            load_model.model_cache = {}
            
        if model_name in load_model.model_cache:
            current_model = load_model.model_cache[model_name]
            current_model_name = model_name
            return current_model
            
        # Find the .gguf file that matches the model name
        model_files = [f for f in os.listdir(MODELS_DIR) if f.endswith('.gguf') and f.startswith(model_name)]
        
        if not model_files:
            raise ValueError(f"No .gguf file found for model: {model_name}")
        
        if len(model_files) > 1:
            app_logger.warning(f"Multiple .gguf files found for model {model_name}. Using the first one.")
        
        selected_model_file = model_files[0]
        selected_model_path = os.path.join(MODELS_DIR, selected_model_file)
        
        # Ensure the path uses forward slashes
        selected_model_path = selected_model_path.replace("\\", "/")
        
        app_logger.info(f"Loading model: {selected_model_path}")
        
        # Configure model parameters
        model_params = {
            "model_path": selected_model_path,
            "n_ctx": 4096,
            "n_threads": 8,
            "seed": 42,
            "f16_kv": True,
            "use_mlock": True
        }
        
        # Load the model with the appropriate configuration
        current_model = Llama(**model_params)
        current_model_name = model_name
        load_model.model_cache[model_name] = current_model
    return current_model

# Get list of available AI models
def get_available_models():
    return [f for f in os.listdir(MODELS_DIR) if f.endswith('.gguf')]

# Validate model selection and return appropriate error response if validation fails
def validate_model_selection(model_name, operation_name="operation"):

    # Check if model is provided and valid
    if not model_name or model_name.strip() == '':
        app_logger.warning(f"No model selected for {operation_name}")
        return False, jsonify({
            'status': 'error',
            'message': 'No AI model selected. Please select a model from the dropdown menu.'
        }), 400
    
    # Check if the model exists in the available models
    model_files = get_available_models()
    if model_name not in model_files:
        app_logger.warning(f"Selected model '{model_name}' not found in available models for {operation_name}")
        return False, jsonify({
            'status': 'error',
            'message': f'Model "{model_name}" not found. Please select an available model.'
        }), 400
    
    return True, None

# Serve the main HTML page
@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'chat-interface.html')

## Model-related routes

# Get available models and current model, current model is returned so the dropdown in the UI will auto-select it
@app.route('/models')
def models():
    available_models = get_available_models()
    if not available_models:
        return jsonify({"error": "No AI models found in the ai_models folder."}), 404
    return jsonify({
        "models": available_models,
        "current_model": current_model_name
    })

# Get the path to the models folder
@app.route('/models/folder_path', methods=['GET'])
def get_models_folder_path():
    return jsonify({'path': os.path.abspath(MODELS_DIR)})

# Open the models folder in the file explorer
@app.route('/models/open_folder', methods=['POST'])
def open_models_folder():
    try:
        if os.name == 'nt':  # Windows
            os.startfile(MODELS_DIR)
        elif os.name == 'posix':  # macOS and Linux
            subprocess.call(['open', MODELS_DIR])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

## Conversation-related routes
# operations involving more than one conversation use /conversations for example getting a list of all conversations or switching between 2 conversations
# operations involving one conversation, usually with a supplied conversation id from the client, use /conversation singular

# Get all conversations
@app.route('/conversations', methods=['GET'])
def get_conversations():
    conversations_with_warnings = load_all_conversations(CONVERSATIONS_DIR)
    return jsonify([{
        'id': conv.id,
        'name': conv.name,
        'latest_message_timestamp': conv.latest_message_timestamp.isoformat() if conv.latest_message_timestamp else None,
        'version_warning': warning
    } for conv, warning in conversations_with_warnings])

# Switch to a different conversation
@app.route('/conversations/switch', methods=['POST'])
def switch_conversation():
    global current_conversation
    conversation_id = request.json['id']
    if current_conversation:
        save_conversation(current_conversation, CONVERSATIONS_DIR)
    
    loaded_conversation, version_warning = load_conversation(conversation_id, CONVERSATIONS_DIR)
    
    if not loaded_conversation:
        # The conversation was deleted due to version incompatibility
        return jsonify({
            'success': False,
            'error': version_warning or "Conversation could not be loaded"
        }), 404
    
    current_conversation = loaded_conversation
    
    return jsonify({
        'success': True,
        'conversation_id': current_conversation.id,
        'conversation_name': current_conversation.name,
        'version_warning': version_warning,
        'branch': [
            {
                'id': node.id,
                'content': node.content,
                'sender': node.sender,
                'timestamp': node.timestamp.isoformat(),
                'model_name': node.model_name,
                'internal_monologue': node.internal_monologue
            } for node in current_conversation.get_current_branch()
        ]
    })


# Get the current conversation
@app.route('/conversations/current', methods=['GET'])
def get_current_conversation():
    if current_conversation:
        # Check if the current conversation needs a version update
        version_parts = [int(p) for p in CONVERSATION_VERSION.split('.')]
        conv_parts = [int(p) for p in current_conversation.version.split('.')] if hasattr(current_conversation, 'version') else [0, 0, 0]
        
        version_warning = None
        if conv_parts[1] < version_parts[1]:
            # Minor version difference send warning message
            version_warning = f"This conversation was created with an older version (v{current_conversation.version if hasattr(current_conversation, 'version') else '0.0.0'}). Some features may not work as expected."
        
        return jsonify({
            'conversation_id': current_conversation.id,
            'conversation_name': current_conversation.name,
            'version_warning': version_warning,
            'branch': [
                {
                    'id': node.id,
                    'content': node.content,
                    'sender': node.sender,
                    'timestamp': node.timestamp.isoformat(),
                    'model_name': node.model_name,
                    'internal_monologue': node.internal_monologue
                } for node in current_conversation.get_current_branch()
            ]
        })
    else:
        return jsonify({'conversation_id': None, 'conversation_name': None, 'branch': [], 'version_warning': None})

# Get sibling messages for a given node
@app.route('/conversations/get_siblings', methods=['POST'])
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
                    'model_name': node.model_name,
                    'internal_monologue': node.internal_monologue
                } for node in siblings
            ]
        })
    
    return jsonify({'siblings': []}), 400

# Delete a conversation
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

# Clear the current conversation variable, this does not effect the conversation itself
@app.route('/conversation/clear', methods=['POST'])
def clear_conversation():
    global current_conversation
    if current_conversation:
        save_conversation(current_conversation, CONVERSATIONS_DIR)
    current_conversation = None
    return jsonify({'success': True})

# Rename a conversation
@app.route('/conversation/rename', methods=['POST'])
def rename_conversation():
    data = request.json
    conversation_id = data['conversation_id']
    new_name = data['new_name']
    
    try:
        conversation, warning = load_conversation(conversation_id, CONVERSATIONS_DIR)
        if not conversation:
            return jsonify({'success': False, 'error': warning or "Conversation not found"}), 404
            
        conversation.set_name(new_name)
        save_conversation(conversation, CONVERSATIONS_DIR)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# Switch to a different branch in the conversation
@app.route('/conversation/switch_branch', methods=['POST'])
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
                    'model_name': node.model_name,
                    'internal_monologue': node.internal_monologue
                } for node in current_conversation.get_current_branch()
            ]
        })
    
    return jsonify({'success': False, 'error': 'No active conversation'}), 400

# Add a user message to the conversation
@app.route('/conversation/add_user_message', methods=['POST'])
def add_user_message():
    request_start = time.time()
    global current_session_prompt, current_model, current_conversation, current_model_name
    data = request.json
    user_input = data['message']
    model_name = data['model']
    
    # Validate model selection
    is_valid, error_response = validate_model_selection(model_name, "message generation")
    if not is_valid:
        return error_response
    
    if 'session_prompt' in data:
        current_session_prompt = data['session_prompt']
    
    def generate(user_input, model_name):
        global current_model, current_conversation, current_model_name
        
        if current_model is None or current_model_name != model_name:
            yield json.dumps({"status": "loading_model"})
            model_load_start = time.time()
            current_model = load_model(model_name)
            current_model_name = model_name
            app_logger.info(f"Model loading took {time.time() - model_load_start:.4f} seconds")
        
        if current_conversation is None:
            yield json.dumps({"status": "creating_conversation"})
            naming_start = time.time()
            naming_prompt = f"{NAMING_PROMPT}\n\nUser's message: {user_input}\n\nTitle:"
            naming_response = current_model(naming_prompt, max_tokens=10, stop=["\n"], temperature=0.7)
            conversation_name = naming_response['choices'][0]['text'].strip()
            current_conversation = create_conversation(conversation_name)
            app_logger.info(f"Conversation creation and naming took {time.time() - naming_start:.4f} seconds")
        
        save_start = time.time()
        new_node = current_conversation.add_message(user_input, "Human")
        save_conversation(current_conversation, CONVERSATIONS_DIR)
        app_logger.info(f"Saving user message took {time.time() - save_start:.4f} seconds")
        
        total_time = time.time() - request_start
        app_logger.info(f"Total user message processing took {total_time:.4f} seconds")
        
        yield json.dumps({
            "status": "complete",
            "conversation_id": current_conversation.id,
            "conversation_name": current_conversation.name,
            "human_node_id": new_node.id,
            "timestamp": new_node.timestamp.isoformat()
        })
    
    return Response(generate(user_input, model_name), mimetype='application/json')

# Get AI response for the current conversation
@app.route('/conversation/get_ai_response', methods=['POST'])
def get_ai_response():
    global current_conversation
    data = request.json
    conversation_id = data['conversation_id']
    model_name = data['model']
    planning_mode = data.get('planning_mode', False)
    
    # Validate model selection
    is_valid, error_response = validate_model_selection(model_name, "AI response generation")
    if not is_valid:
        return error_response
    
    if current_conversation.id != conversation_id:
        current_conversation = load_conversation(conversation_id, CONVERSATIONS_DIR)
    
    return Response(generate_ai_response(current_conversation, model_name, planning_mode), mimetype='application/json')

# Regenerate AI response for a specific message
@app.route('/message/regenerate', methods=['POST'])
def regenerate_response():
    data = request.json
    node_id = data['node_id']
    model_name = data['model']
    planning_mode = data.get('planning_mode', False)
    
    # Validate model selection
    is_valid, error_response = validate_model_selection(model_name, "response regeneration")
    if not is_valid:
        return error_response
    
    if current_conversation:
        node_to_regenerate = current_conversation.find_node(node_id)
        if node_to_regenerate and node_to_regenerate.parent:
            current_conversation.tree.current_node = node_to_regenerate.parent
            return Response(generate_ai_response(current_conversation, model_name, planning_mode), mimetype='application/json')
    
    return jsonify({'success': False, 'error': 'Failed to regenerate response'}), 400

# Edit a message in the conversation
@app.route('/message/edit', methods=['POST'])
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

# Get the original content of a message, i.e. plain text instead of formatted markdown
@app.route('/message/get_original_content', methods=['POST'])
def get_original_content():
    data = request.json
    node_id = data['node_id']
    app_logger.info(f"Getting original content for node_id: {node_id}")
    
    if current_conversation:
        node = current_conversation.find_node(node_id)
        if node:
            return jsonify({
                'success': True,
                'content': node.content
            })
    
    return jsonify({'success': False, 'error': 'Node not found'}), 404

## Session prompt routes
# Get the current session prompt
@app.route('/session_prompt', methods=['GET'])
def get_current_session_prompt():
    return jsonify({'session_prompt': current_session_prompt})

# Get the default session prompt
@app.route('/session_prompt/default', methods=['GET'])
def get_default_current_session_prompt():
    return jsonify({'default_session_prompt': DEFAULT_SESSION_PROMPT})

# Set a new session prompt
@app.route('/session_prompt/set', methods=['POST'])
def set_current_session_prompt():
    global current_session_prompt
    data = request.json
    new_current_session_prompt = data.get('session_prompt')
    
    if new_current_session_prompt is not None:
        current_session_prompt = new_current_session_prompt
        app_logger.info(f"New session prompt set: \n {current_session_prompt}")
        return jsonify({'success': True, 'session_prompt': current_session_prompt})
    else:
        return jsonify({'success': False, 'error': 'No session prompt provided'}), 400

# Serve icon files
@app.route('/icon/<path:filename>')
def serve_icon(filename):
    icon_dir = os.path.join(BASE_DIR, 'icon')
    app_logger.info(f"Requested icon file path from: {icon_dir}/{filename}")
    return send_from_directory(icon_dir, filename)

def open_browser():
    """Open browser to the application URL"""
    server_url = 'http://localhost:5000'
    app_logger.info(f"Opening browser to {server_url}")
    
    # Try to open the browser
    try:
        webbrowser.open(server_url)
        app_logger.info("Browser opened successfully")
    except Exception as e:
        app_logger.error(f"Failed to open browser: {str(e)}")

# Variable to track if we've already opened the browser
browser_opened = False

@app.before_request
def open_browser_on_first_request():
    """Open browser on the first request to any route - this ensures server is ready"""
    global browser_opened
    
    # Only open browser if:
    # 1. We haven't opened it yet
    # 2. We're in packaged mode
    # 3. NO_BROWSER_OPEN environment variable is not set
    if not browser_opened and is_packaged() and not os.environ.get('NO_BROWSER_OPEN'):
        # Use a timer to avoid blocking the request
        threading.Timer(0.1, open_browser).start()
        browser_opened = True
        app_logger.info("Browser opening scheduled after first request")

# Function to bootstrap the first request
def trigger_first_request():
    """Make a request to the server to trigger @app.before_request handlers"""
    time.sleep(1.0)  # Give the server a moment to start
    try:
        import urllib.request
        urllib.request.urlopen('http://localhost:5000/', timeout=1)
        app_logger.debug("Bootstrap request completed")
    except Exception as e:
        app_logger.debug(f"Bootstrap request failed: {str(e)}")

if __name__ == '__main__':
    app_logger.info("Application started")
    
    # Log environment information
    app_logger.info(f"Running in {'packaged' if is_packaged() else 'development'} mode")
    app_logger.info(f"Base directory: {BASE_DIR}")
    app_logger.info(f"User data directory: {USER_DATA_DIR}")
    app_logger.info(f"Models directory: {MODELS_DIR}")
    app_logger.info(f"Conversations directory: {CONVERSATIONS_DIR}")
    
    # Ensure directories exist
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(CONVERSATIONS_DIR, exist_ok=True)
    
    # Start a thread to trigger the first request if we're in packaged mode
    if is_packaged() and not os.environ.get('NO_BROWSER_OPEN'):
        bootstrap_thread = threading.Thread(target=trigger_first_request)
        bootstrap_thread.daemon = True
        bootstrap_thread.start()
        app_logger.info("Bootstrap thread started")
    
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)