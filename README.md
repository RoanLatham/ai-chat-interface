<p align="center">
  <img src="./icon/AII-icon.ico" alt="Local AI Chat Logo" width="72"/>
</p>

<h1 align="center">Local AI Chat</h1>

<p align="center">
  A privacy-focused conversational AI app powered by local LLMs, featuring branching conversations
</p>
<p align="center">
  Built with 1 HTML file and 1 Python script
</p>

<p align="center">
  <img alt="GitHub License" src="https://img.shields.io/badge/License-MIT-green">
  <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/RoanLatham/ai-chat-interface">
  <img alt="GitHub issues" src="https://img.shields.io/github/issues/RoanLatham/ai-chat-interface">
</p>

<p align="center">
  <img alt="Flask" src="https://img.shields.io/badge/Flask-v3.0.0-blue">
  <img alt="llama-cpp-python" src="https://img.shields.io/badge/llama--cpp--python-v0.3.5-blue">
  <img alt="Python" src="https://img.shields.io/badge/Python-v3.11.7-blue">
</p>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#development">Development</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

<details open>
<summary><h2>✨ Key Features</h2></summary>

- **🔒 Completely Local & Private** - All processing happens on your machine with no data shared externally
- **🧠 Multiple AI Model Support** - Use different GGUF-format models suited to your hardware and requirements
- **🌿 Branching Conversations** - Explore different responses and maintain multiple conversation paths
- **⚙️ Custom System Prompts** - Tailor your AI's behavior and capabilities
- **📝 Markdown Rendering** - Beautiful formatting of AI responses with syntax highlighting
- **💻 Code Syntax Highlighting** - Clear, readable code snippets in responses
- **🌐 Web-Based Interface** - Intuitive browser UI with no installation requirements
- **💾 Conversation Management** - Save, load, and organize your conversation history
- **🔄 Versioning System** - Ensures backward compatibility of conversation files
- **🛠️ Developer Tools** - Advanced editing and management for conversation files

</details>

<details open>
<summary><h2>📦 Installation</h2></summary>

### Prerequisites

- Windows 10/11 (for packaged versions) or any Windows/Linux/macOS system (for source installation)
- Python minimum 3.6 or higher (if running from source)
- GGUF-format language models

### Windows Only: Packaged Versions

<details>
<summary><h4>💼 Portable Version</h4></summary>

1. Download the portable ZIP from the [Releases](https://github.com/RoanLatham/ai-chat-interface/releases) page
2. Extract to any location
3. Run `LocalAIChat.exe`

</details>

<details>
<summary><h4>💿 Windows Installer</h4></summary>

1. Download the latest installer from the [Releases](https://github.com/RoanLatham/ai-chat-interface/releases) page
2. Run the installer and follow the on-screen instructions
3. Launch the application from the Start Menu or Desktop shortcut

</details>

<details>
<summary><h3>📦 All Platforms: From Source</h3></summary>

This method works on Windows, macOS, and Linux.

```bash
# Clone the repository
git clone https://github.com/RoanLatham/ai-chat-interface.git

# Navigate to the project directory
cd ai-chat-interface

# Optional but recommended: Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate.ps1
# On macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python local-ai-chat-app.py
```

</details>

<details>
<summary><h4>🤖 Setting Up AI Models</h4></summary>

After installation:

1. Place GGUF model files in the `ai_models` directory
2. Refresh or open the web interface
3. Select your model from the dropdown in the top center of the page

<details>
<summary>🔍 Where to find compatible models</summary>

Compatible GGUF models can be downloaded from:

- [Hugging Face](https://huggingface.co/models?sort=downloads&search=gguf)

Recommended starter models:

- Llama-3-8B-Instruct (various quantizations)
- Mistral-7B-Instruct (various quantizations)
- Phi-3-mini-4k-instruct (various quantizations)

Choose quantization level based on your hardware capabilities:

- Q4_K_M: Good balance of quality and performance
- Q5_K_M: Better quality, more memory usage
- Q8_0: High quality, requires more memory, storage, and compute

</details>

</details>

</details>

<details open>
<summary><h2>🚀 Usage</h2></summary>

<details>
<summary><h4>🚀 Starting the Application</h4></summary>

1. Launch the application using the desktop shortcut or executable
2. A browser window will automatically open to `http://localhost:5000`
3. If the browser doesn't open automatically, manually navigate to this address

</details>

<details>
<summary><h4>✨ Features</h4></summary>

<details>
<summary>💬 Creating a New Conversation</summary>

1. Click on the "New Conversation" button in the sidebar
2. Start typing a message and press Enter or click Send
3. Wait for the AI to generate a response

</details>

<details>
<summary>🌿 Working with Branches</summary>

1. To edit a message and create a new branch, click the "Edit" button on any message
2. To regenerate an AI response, click the "Regenerate" button
3. Navigate between branches using the left/right arrows that appear at branching points

</details>

<details>
<summary>🔀 Using Different Models</summary>

1. Select a model from the dropdown menu in the upper-right corner
2. The model will be loaded when you send your next message

</details>

<details>
<summary>⚙️ Customizing System Prompts</summary>

1. Click the "Edit System Prompt" button in the header
2. Modify the prompt as desired
3. Click "Save" to apply the changes

</details>

<details>
<summary><h4>📂 Managing Conversations</h4></summary>

- **✏️ Rename**: Click the menu icon next to a conversation and select "Rename"
- **🗑️ Delete**: Click the menu icon next to a conversation and select "Delete"
- **🔀 Switch Branches**: Navigate to a specific branch using the branch indicators in the chat

</details>

</details>

<details>
<summary><h4>⚠️ Troubleshooting</h4></summary>

- If models aren't appearing, ensure they're placed in the `ai_models` directory with a `.gguf` extension
- For slow responses, try a smaller or more optimized model
- Check the `logs` directory for detailed error information

</details>

</details>

<details open>
<summary><h2>📝 Documentation</h2></summary>

- [Local AI Chat App Documentation](./Docs/local_ai_chat_app_documentation.md) - Core application functionality
- [Conversation Module Documentation](./Docs/conversation_module_documentation.md) - Conversation data structure
- [Conversation Versioning Documentation](./Docs/conversation_versioning.md) - File compatibility system
- [Conversation Editor Documentation](./Docs/conversation_editor_documentation.md) - Developer tools

</details>

<details open>
<summary><h2>💻 Development</h2></summary>

<details>
<summary><h4>📁 Project Structure</h4></summary>

```
ai-chat-interface/
├── ai_models/             # AI model files (.gguf)
├── build_tools/           # Packaging and build scripts
├── conversations/         # Saved conversation files
├── example_conversations/ # Conversation files included in the build process
├── docs/                  # Documentation files
├── icon/                  # Application icons
├── logs/                  # Application logs
├── local-ai-chat-app.py   # Main application
├── conversation.py        # Conversation data structure
├── chat-interface.html    # Web interface
├── system-prompt.txt      # Top-level AI system prompt
└── requirements.txt       # Python dependencies
```

</details>

<details>
<summary><h4>🔨 Building the Application</h4></summary>

```bash
# Navigate to the build_tools directory
cd build_tools

# Run the master build script
python build_master.bat

# Build without creating an installer
python build_master.bat --no-installer

# Skip dependency checks
python build_master.bat --skip-deps
```

</details>

<details>
<summary><h4>🔧 Conversation Editor Tool</h4></summary>

The project includes a developer tool for managing conversation files:

```bash
# Run the conversation editor
python conversation_editor.py

# Open a specific conversation file
python conversation_editor.py path/to/conversation.pickle

# Set version for a file without launching interactive mode
python conversation_editor.py path/to/conversation.pickle --set-version 1.1.0
```

See [Conversation Editor Documentation](./Docs/conversation_editor_documentation.md) for more details

</details>

</details>

<details open>
<summary><h2>🤝 Contributing</h2></summary>

Contributions to improve Local AI Chat are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

Before submitting, please ensure:

- Your code follows the project's coding style
- You've added/updated documentation as necessary

</details>

<details open>
<summary><h2>📄 License</h2></summary>

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

</details>

<details open>
<summary><h2>👏 Acknowledgements</h2></summary>

- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) - Python bindings for llama.cpp
- [Flask](https://flask.palletsprojects.com/) - Server framework
- [Marked.js](https://marked.js.org/) - Markdown parser
- [Highlight.js](https://highlightjs.org/) - Syntax highlighting

</details>

---

<div align="center">
Made with ❤️ by Roan Latham

[Report Bug](https://github.com/RoanLatham/ai-chat-interface/issues) · [Request Feature](https://github.com/RoanLatham/ai-chat-interface/issues)

</div>
