<p align="center">
  <img src="./icon/AII-icon.ico" alt="Local AI Chat Logo" width="200"/>
</p>

<h1 align="center">Local AI Chat</h1>

<p align="center">
  A privacy-focused conversational AI app powered by local LLMs, featuring branching conversations
  Built with 1 HTML file and 1 Python server
</p>

<p align="center">
  <img alt="GitHub License" src="https://img.shields.io/github/license/RoanLatham/ai-chat-interface">
  <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/RoanLatham/ai-chat-interface">
  <img alt="GitHub issues" src="https://img.shields.io/github/issues/RoanLatham/ai-chat-interface">
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

## Key Features

- **Completely Local & Private** - All processing happens on your machine with no data shared externally
- **Multiple AI Model Support** - Use different GGUF-format models suited to your hardware and requirements
- **Branching Conversations** - Explore different responses and maintain multiple conversation paths
- **Custom System Prompts** - Tailor your AI's behavior and capabilities
- **Markdown Rendering** - Beautiful formatting of AI responses with syntax highlighting
- **Code Syntax Highlighting** - Clear, readable code snippets in responses
- **Web-Based Interface** - Intuitive browser UI with no installation requirements
- **Conversation Management** - Save, load, and organize your conversation history
- **Versioning System** - Ensures backward compatibility of conversation files
- **Developer Tools** - Advanced editing and management for conversation files

## Installation

### Prerequisites

- Windows 10/11 (for packaged versions) or any Windows/Linux/macOS system (for source installation)
- Python 3.8 or higher (if running from source)
- GGUF-format language models

### Windows Only: Packaged Versions

#### Portable Version

1. Download the portable ZIP from the [Releases](https://github.com/RoanLatham/ai-chat-interface/releases) page
2. Extract to any location
3. Run `LocalAIChat.exe`

#### Windows Installer

1. Download the latest installer from the [Releases](https://github.com/RoanLatham/ai-chat-interface/releases) page
2. Run the installer and follow the on-screen instructions
3. Launch the application from the Start Menu or Desktop shortcut

### All Platforms: From Source

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

### Setting Up AI Models

After installation:

1. Place GGUF model files in the `ai_models` directory
2. Refresh or open the web interface
3. Select your model from the dropdown in the top center of the page

<details>
<summary>Where to find compatible models</summary>

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

## Usage

<details>
<summary>Starting the Application</summary>

1. Launch the application using the desktop shortcut or executable
2. A browser window will automatically open to `http://localhost:5000`
3. If the browser doesn't open automatically, manually navigate to this address

</details>

<details>
<summary>Basic Features</summary>

<details>
<summary>Creating a New Conversation</summary>

1. Click on the "New Conversation" button in the sidebar
2. Start typing a message and press Enter or click Send
3. Wait for the AI to generate a response

</details>

<details>
<summary>Working with Branches</summary>

1. To edit a message and create a new branch, click the "Edit" button on any message
2. To regenerate an AI response, click the "Regenerate" button
3. Navigate between branches using the left/right arrows that appear at branching points

</details>

<details>
<summary>Using Different Models</summary>

1. Select a model from the dropdown menu in the upper-right corner
2. The model will be loaded when you send your next message

</details>

<details>
<summary>Customizing System Prompts</summary>

1. Click the "Edit System Prompt" button in the header
2. Modify the prompt as desired
3. Click "Save" to apply the changes

</details>

</details>

<details>
<summary>Managing Conversations</summary>

- **Rename**: Click the menu icon next to a conversation and select "Rename"
- **Delete**: Click the menu icon next to a conversation and select "Delete"
- **Switch Branches**: Navigate to a specific branch using the branch indicators in the chat

</details>

<details>
<summary>Troubleshooting</summary>

- If models aren't appearing, ensure they're placed in the `ai_models` directory with a `.gguf` extension
- For slow responses, try a smaller or more optimized model
- Check the `logs` directory for detailed error information

</details>

</details>

## Documentation

- [Local AI Chat App Documentation](./Docs/local_ai_chat_app_documentation.md) - Core application functionality
- [Conversation Module Documentation](./Docs/conversation_module_documentation.md) - Conversation data structure
- [Conversation Versioning Documentation](./Docs/conversation_versioning.md) - File compatibility system
- [Conversation Editor Documentation](./Docs/conversation_editor_documentation.md) - Developer tools

## Development

### Project Structure

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

### Building the Application

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

### Conversation Editor Tool

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

## Contributing

Contributions to improve Local AI Chat are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

Before submitting, please ensure:

- Your code follows the project's coding style
- You've added/updated documentation as necessary

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) - Python bindings for llama.cpp
- [Flask](https://flask.palletsprojects.com/) - Server framework
- [Marked.js](https://marked.js.org/) - Markdown parser
- [Highlight.js](https://highlightjs.org/) - Syntax highlighting

---

<p align="center">
  Made with ❤️ by Roan Latham
</p>
