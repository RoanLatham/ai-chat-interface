# Local AI Chat Application Documentation

## Overview

The `local-ai-chat-app.py` module implements a Flask-based web server that provides a local interface for interacting with AI language models. It serves as the backend for the Local AI Chat application, managing AI models, conversations, and providing API endpoints for the web frontend.

This application is designed for single-user, local use. It allows users to have text-based conversations with various AI models in their local environment, without requiring internet connectivity or sending data to external services. The app loads and runs models directly on the user's machine, handles conversation management, and serves a web interface for interaction.

The server is responsible for:

- Managing AI model loading and inference
- Storing and retrieving conversation history
- Processing user inputs and generating AI responses
- Serving the web interface for user interaction
- Handling system settings like custom prompts

## Features & Functionality

### Core Features

- **Local AI Model Integration**: Loads and manages GGUF format language models
- **Conversation Management**: Creates, saves, and loads conversation trees
- **Branching Dialogue Support**: Maintains multiple conversation paths
- **Web Interface**: Serves a browser-based UI for interaction
- **System Prompt Customization**: Allows custom instructions for AI behavior
- **Auto-Naming**: Automatically generates names for new conversations
- **Versioning Support**: Handles conversation format versioning

### Integration Points

The application integrates with:

- **Conversation Module**: Uses the conversation.py module for data structures ([Documentation](GitIgnore/Docs/conversation_module_documentation.md))
- **llama-cpp-python**: Interfaces with AI models through the llama_cpp Python bindings
- **Flask**: Provides the web server and API endpoints
- **Browser Interface**: Serves and communicates with the HTML/JS frontend

## Key Components & Functions

### Application Structure

The application follows a Flask server structure with the following key components:

1. **Initialization and Configuration**: Sets up paths, logging, and globals
2. **Model Management**: Functions for loading and managing AI models
3. **Conversation Handling**: Functions for creating and modifying conversations
4. **API Endpoints**: Flask routes for web interface communication
5. **Prompt Management**: System prompt handling
6. **Response Generation**: AI inference logic

### Global Variables and Constants

| Variable/Constant       | Type           | Description                         |
| ----------------------- | -------------- | ----------------------------------- |
| `MODELS_DIR`            | `str`          | Directory containing AI model files |
| `CONVERSATIONS_DIR`     | `str`          | Directory for saved conversations   |
| `SYSTEM_PROMPT_PATH`    | `str`          | Path to the system prompt file      |
| `current_model`         | `Llama`        | Currently loaded AI model instance  |
| `current_model_name`    | `str`          | Name of the currently loaded model  |
| `current_conversation`  | `Conversation` | Currently active conversation       |
| `current_system_prompt` | `str`          | Currently active system prompt      |

### Utility Functions

| Function               | Description                                 |
| ---------------------- | ------------------------------------------- |
| `is_packaged()`        | Checks if running as a packaged executable  |
| `get_base_dir()`       | Gets the base directory for the application |
| `get_user_data_dir()`  | Gets the user data directory                |
| `setup_logging()`      | Configures logging for the application      |
| `load_system_prompt()` | Loads the system prompt from file           |
| `tokenize(text)`       | Tokenizes text using the current model      |
| `count_tokens(text)`   | Counts tokens in a text string              |

### Model Management

| Function                 | Description                                 |
| ------------------------ | ------------------------------------------- |
| `load_model(model_name)` | Loads an AI model from the models directory |
| `get_available_models()` | Returns a list of available AI models       |

### Prompt Processing

| Function                                                                       | Description                                      |
| ------------------------------------------------------------------------------ | ------------------------------------------------ |
| `prepare_gatt_history(conversation, token_limits)`                             | Prepares conversation history in the GAtt format |
| `prepare_full_prompt(history, token_limits, internal_thought)`                 | Creates the complete prompt for AI generation    |
| `generate_internal_thought(model, conversation, token_limits)`                 | Generates AI internal thought process            |
| `generate_final_response(model, conversation, internal_thought, token_limits)` | Generates the final AI response                  |

### Response Generation

| Function                                                       | Description                               |
| -------------------------------------------------------------- | ----------------------------------------- |
| `generate_ai_response(conversation, model_name, token_limits)` | Main function for generating AI responses |
| `@dataclass TokenLimits`                                       | Dataclass for token limit configuration   |

### API Endpoints

#### General Routes

| Route                   | Method | Description                    |
| ----------------------- | ------ | ------------------------------ |
| `/`                     | GET    | Serves the main HTML interface |
| `/icon/<path:filename>` | GET    | Serves icon files              |

#### Model Management Routes

| Route                 | Method | Description                              |
| --------------------- | ------ | ---------------------------------------- |
| `/models`             | GET    | Gets available models and current model  |
| `/models/folder_path` | GET    | Gets the path to the models folder       |
| `/models/open_folder` | POST   | Opens the models folder in file explorer |

#### Conversation Management Routes

| Route                         | Method | Description                              |
| ----------------------------- | ------ | ---------------------------------------- |
| `/conversations`              | GET    | Gets all conversations                   |
| `/conversations/current`      | GET    | Gets the current conversation            |
| `/conversations/get_siblings` | POST   | Gets sibling messages for a node         |
| `/conversations/switch`       | POST   | Switches to a different conversation     |
| `/conversation/delete`        | POST   | Deletes a conversation                   |
| `/conversation/clear`         | POST   | Clears the current conversation variable |
| `/conversation/rename`        | POST   | Renames a conversation                   |
| `/conversation/switch_branch` | POST   | Switches to a different branch           |

#### Message Routes

| Route                            | Method | Description                               |
| -------------------------------- | ------ | ----------------------------------------- |
| `/conversation/add_user_message` | POST   | Adds a user message to conversation       |
| `/conversation/get_ai_response`  | POST   | Gets AI response for current conversation |
| `/message/regenerate`            | POST   | Regenerates AI response for a message     |
| `/message/edit`                  | POST   | Edits a message in the conversation       |
| `/message/get_original_content`  | POST   | Gets original message content             |

#### System Prompt Routes

| Route                    | Method | Description                    |
| ------------------------ | ------ | ------------------------------ |
| `/system_prompt`         | GET    | Gets the current system prompt |
| `/system_prompt/default` | GET    | Gets the default system prompt |
| `/system_prompt/set`     | POST   | Sets a new system prompt       |

## Usage Guide

### Starting the Application

The application can be run directly or as a packaged executable:

```python
# Run directly
python local-ai-chat-app.py

# With browser auto-open disabled
NO_BROWSER_OPEN=1 python local-ai-chat-app.py
```

When started, the application:

1. Sets up logging
2. Initializes directories
3. Loads available models
4. Starts the Flask server on port 5000
5. Opens a browser to the interface (unless disabled)

### Interacting with the API

Developers can interact with the API endpoints to build custom interfaces or extend functionality:

```javascript
// Example: Load the current conversation
fetch("/conversations/current")
  .then((response) => response.json())
  .then((data) => {
    if (data.conversation_id) {
      console.log(`Loaded conversation: ${data.conversation_name}`);
      // Process conversation data
    }
  });

// Example: Send a user message
fetch("/conversation/add_user_message", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    message: "Hello, AI!",
    model: "llama-3-8b",
  }),
})
  .then((response) => response.json())
  .then((data) => {
    console.log(`Message added with ID: ${data.human_node_id}`);
    // Process response
  });
```

### Handling Streaming Responses

The application uses a streaming response pattern for long-running operations:

```javascript
// Example: Process streaming AI response
const eventSource = new EventSource("/conversation/get_ai_response");

eventSource.onmessage = function (event) {
  const data = JSON.parse(event.data);

  if (data.status === "loading_model") {
    console.log("Loading model...");
  } else if (data.status === "generating") {
    console.log("Generating response...");
  } else if (data.status === "complete") {
    console.log(`Response: ${data.response}`);
    eventSource.close();
  }
};
```

## Customization & Configuration

### Environment Variables

| Variable          | Description                                |
| ----------------- | ------------------------------------------ |
| `NO_BROWSER_OPEN` | Set to "1" to prevent browser auto-opening |

### Directories and Files

| Path                | Description         | Default Location              |
| ------------------- | ------------------- | ----------------------------- |
| `/ai_models/`       | GGUF model files    | `<app_dir>/ai_models/`        |
| `/conversations/`   | Saved conversations | `<app_dir>/conversations/`    |
| `/logs/`            | Application logs    | `<app_dir>/logs/`             |
| `system-prompt.txt` | System prompt file  | `<app_dir>/system-prompt.txt` |

### Prompts and System Messages

The application uses several prompts that can be customized:

1. **System Prompt**: Main instructions for the AI's behavior
2. **Naming Prompt**: Used to generate conversation names
3. **Internal Thought Prompt**: Guides AI's internal reasoning

These can be modified in the code or, for the system prompt, by editing the `system-prompt.txt` file.

### Model Parameters

Model loading parameters can be adjusted in the `load_model()` function:

```python
model_params = {
    "model_path": selected_model_path,
    "n_ctx": 4096,         # Context window size
    "n_threads": 8,        # Processing threads
    "seed": 42,            # Random seed
    "f16_kv": True,        # Use FP16 for key/value cache
    "use_mlock": True      # Lock memory to prevent swapping
}
```

## Best Practices & Recommendations

### Performance Optimization

1. **Model Management**:

   - Only load models when needed
   - Use quantized models (Q4_K_M, Q5_K_M) for better performance
   - Adjust thread count based on system capabilities

2. **Token Management**:

   - Be mindful of context window limits
   - Use the TokenLimits class to manage token usage
   - Trim conversation history when needed

3. **Resource Usage**:
   - Close the application when not in use to free resources
   - Avoid loading multiple large models in a single session
   - Consider pruning old conversation branches

### Development Extensions

1. **Adding New Features**:

   - Add new routes in the Flask application
   - Follow the existing pattern for streaming responses
   - Update the web interface in chat-interface.html

2. **Error Handling**:

   - Check for errors in model loading
   - Validate inputs in API endpoints
   - Use try/except blocks for file operations

3. **Testing**:
   - Test with various model sizes
   - Verify conversation saving/loading
   - Check browser compatibility

## Error Handling & Troubleshooting

### Common Issues

| Issue                   | Possible Causes                         | Solutions                                         |
| ----------------------- | --------------------------------------- | ------------------------------------------------- |
| Server won't start      | Port conflict                           | Change Flask port or close competing applications |
| Model loading fails     | Invalid or missing model file           | Check model file exists and has .gguf extension   |
| Out of memory errors    | Model too large for system              | Use a smaller or more quantized model             |
| Browser doesn't open    | Environment setting or permission issue | Manually navigate to http://localhost:5000        |
| Conversation not saving | Directory permission issues             | Check permissions on conversations directory      |

### Log Files

Application logs are stored in the `logs/app.log` file with rotation. Check these logs for detailed error information when troubleshooting.

### Debugging

For development purposes, you can enable Flask debug mode by setting `debug=True` in the `app.run()` call. This provides more detailed error information in the browser.

## Additional Notes

### Single-User Design

The application is designed for local, single-user use. It:

- Uses in-memory globals for current state
- Does not implement authentication or user sessions
- Assumes exclusive access to model and conversation files

### Browser Interface

The web interface is served from a static HTML file (`chat-interface.html`) that communicates with the Flask backend via API calls. No separate web server is required.

### Packaging

The application can be packaged into a standalone executable using PyInstaller. When running in packaged mode:

- Paths are adjusted to work relative to the executable
- Resource files are bundled with the application
- Browser is automatically opened at startup

### Key Dependencies

The application relies on the following key external libraries:

- **Flask**: Web server framework
- **llama-cpp-python**: Python bindings for llama.cpp
- **Conversation Module**: Custom module for conversation management

### Related Documentation

- [Conversation Module Documentation](GitIgnore/Docs/conversation_module_documentation.md) - Documentation for the conversation data structures
- [Conversation Editor Documentation](GitIgnore/Docs/conversation_editor_documentation.md) - Documentation for the conversation editor tool
