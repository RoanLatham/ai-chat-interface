import os
from flask import Flask, request, jsonify, send_from_directory
from llama_cpp import Llama

app = Flask(__name__)

# Directory containing AI models
MODELS_DIR = "ai_models"
current_model = None
current_model_name = None

DEFAULT_SYSTEM_PROMPT = """You are a helpful, respectful, and honest AI assistant. Always provide accurate information and if you're unsure, admit it. Prioritize user safety and well-being in your responses. Be concise yet informative, and tailor your language to the user's level of understanding. Respect privacy and ethical boundaries in your interactions."""

current_system_prompt = DEFAULT_SYSTEM_PROMPT

def load_model(model_name):
    global current_model, current_model_name
    if current_model_name != model_name:
        selected_model_path = os.path.join(MODELS_DIR, model_name)
        # Convert backslashes to forward slashes and ensure it starts with "./"
        selected_model_path = "./" + selected_model_path.replace("\\", "/")
        print(f"Loading model: {selected_model_path}")
        current_model = Llama(model_path=selected_model_path, n_ctx=2048)
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

@app.route('/chat', methods=['POST'])
def chat():
    global current_system_prompt, current_model, current_model_name
    data = request.json
    user_input = data['message']
    model_name = data['model']
    if 'system_prompt' in data:
        current_system_prompt = data['system_prompt']
    
    if current_model is None or current_model_name != model_name:
        current_model = load_model(model_name)
    
    full_prompt = f"{current_system_prompt}\n\nHuman: {user_input}\nAI:"
    response = current_model(full_prompt, max_tokens=100, stop=["Human:", "\n"], echo=True)
    ai_response = response['choices'][0]['text'].split("AI:")[-1].strip()
    
    return jsonify({'response': ai_response})

@app.route('/system_prompt', methods=['GET'])
def get_system_prompt():
    return jsonify({'system_prompt': current_system_prompt})

if __name__ == '__main__':
    app.run(debug=True)
