import os
from flask import Flask, request, jsonify, send_from_directory
from llama_cpp import Llama
from Conversation import Conversation, create_conversation, save_conversation

app = Flask(__name__)

# Directory containing AI models
MODELS_DIR = "ai_models"
# Directory containing AI conversations
CONVERSATIONS_DIR = "./conversations"

current_model = None
current_model_name = None

current_conversation = None

SUPER_SYSTEM_PROMPT = """
You are an AI assistant with advanced conversational capabilities. Your responses should adhere to the following guidelines:

1. Context Awareness: The input you receive will be structured as follows:
   [System Prompt]
   [Conversation History]{
   - ai: [previous AI Response]
   - Human: [previous User Message]
   }
   Human: [Latest User Message]

2. Memory and Retrieval: Actively remember details from the entire conversation history. When asked about previous information, retrieve and use it accurately.

3. Response Format: Your responses should be clear, concise, and directly address the user's input. Do not include labels like "AI:" in your response.

4. Adaptability: Tailor your language and complexity to match the user's level of understanding, which may vary throughout the conversation.

5. Task Completion: If given a task or asked to remember specific information, confirm your understanding and recall it accurately when prompted later.

6. Honesty and Uncertainty: If you're unsure about something, admit it clearly. Do not fabricate information.

7. Safety and Ethics: Prioritize user safety and well-being. Respect privacy and ethical boundaries in all interactions.

8. Contextual Continuity: Maintain coherence with the ongoing conversation. Reference previous points when relevant.

9. Instruction Following: Adhere to any specific instructions provided in the system prompt or by the user during the conversation.

10. Conciseness: Provide informative responses while being as concise as possible, unless the user explicitly requests more detailed information.

Always strive to be helpful, respectful, and honest in your interactions.
"""

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
    global current_system_prompt, current_model, current_conversation, current_model_name
    data = request.json
    user_input = data['message']
    model_name = data['model']
    if 'system_prompt' in data:
        current_system_prompt = data['system_prompt']
    
    if current_model is None or current_model_name != model_name:
        current_model = load_model(model_name)
    
    if current_conversation is None:
        current_conversation = create_conversation("New Conversation")
    
    current_conversation.add_message(user_input, "Human")
    
    conversation_history = "\n".join([f"{node.sender}: {node.content}" for node in current_conversation.get_current_branch()])
    full_prompt = f"{SUPER_SYSTEM_PROMPT}\n\n{current_system_prompt}\n\n{conversation_history}\nHuman: {user_input}\nAI:"
    print(full_prompt)
    
    response = current_model(full_prompt, max_tokens=100, stop=["Human:", "\n"], echo=True)
    ai_response = response['choices'][0]['text'].split("AI:")[-1].strip()
    
    current_conversation.add_message(ai_response, "AI")
    save_conversation(current_conversation, CONVERSATIONS_DIR)
    
    return jsonify({'response': ai_response})

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
