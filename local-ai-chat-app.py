import os
from flask import Flask, request, jsonify, send_from_directory
from llama_cpp import Llama

app = Flask(__name__)

# Directory containing AI models
MODELS_DIR = "ai_models"

# Dictionary to store loaded models
loaded_models = {}

def load_model(model_path):
    if model_path not in loaded_models:
        loaded_models[model_path] = Llama(model_path=model_path, n_ctx=2048)
    return loaded_models[model_path]

def get_available_models():
    return [f for f in os.listdir(MODELS_DIR) if f.endswith('.bin')]

@app.route('/')
def index():
    return send_from_directory('.', 'chat-interface.html')

@app.route('/models')
def models():
    return jsonify(get_available_models())

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data['message']
    model_name = data['model']
    
    model_path = os.path.join(MODELS_DIR, model_name)
    llm = load_model(model_path)
    
    # Generate response from the selected model
    response = llm(f"Human: {user_input}\nAI:", max_tokens=100, stop=["Human:", "\n"], echo=True)
    ai_response = response['choices'][0]['text'].split("AI:")[-1].strip()
    
    return jsonify({'response': ai_response})

if __name__ == '__main__':
    app.run(debug=True)
