# Conversation Editor Documentation

## Overview

The Conversation Editor is a development and maintenance tool designed for manually editing and manipulating conversation pickle files used by the Local AI Chat application. It provides a command-line interface for browsing, editing, and managing conversation trees, enabling developers and power users to perform operations that aren't available through the standard chat interface.

This tool is particularly useful for diagnosing issues, recovering from corrupted conversations, pruning unwanted branches, and performing batch operations on conversation data.

## Features & Functionality

The Conversation Editor offers a comprehensive set of features for managing conversation files:

- **File Management**: Load and save conversation pickle files
- **Tree Navigation**: Traverse through conversation nodes using a branch-aware interface
- **Content Editing**: View and modify message content, including AI internal monologues
- **Structure Manipulation**: Delete nodes, prune branches, and reorganize conversation trees
- **Metadata Operations**: Update conversation name, version, and custom metadata
- **Batch Processing**: View directory contents and perform operations across multiple files
- **Version Management**: View and update conversation version information

The editor integrates with the `conversation.py` module from the main application but can also function independently with a minimal built-in implementation of conversation classes.

## Key Components & Functions

### Core Classes

#### `ConversationEditor`

The main class that encapsulates the editor's functionality.

**Key Methods:**

| Method                           | Purpose                                                    |
| -------------------------------- | ---------------------------------------------------------- |
| `load_pickle(file_path)`         | Loads a conversation pickle file into memory               |
| `save_pickle(file_path)`         | Saves the current conversation to a pickle file            |
| `regenerate_id()`                | Creates a new UUID for the conversation                    |
| `print_tree()`                   | Displays the entire conversation tree structure            |
| `view_node(node_id)`             | Shows detailed information about a specific node           |
| `print_branch()`                 | Displays the current branch from root to current node      |
| `view_directory(directory_path)` | Lists all conversation files in a directory                |
| `navigate_to_child(index)`       | Moves to a child node by index                             |
| `navigate_to_parent()`           | Moves to the parent of the current node                    |
| `edit_node_content(content)`     | Updates the content of the current node                    |
| `delete_node(node_id)`           | Removes a node and its children from the tree              |
| `prune_to_current_branch()`      | Keeps only the current branch, deleting all other branches |
| `set_version(new_version)`       | Updates the conversation version                           |
| `update_metadata(key, value)`    | Sets or updates a metadata field                           |
| `interactive_mode()`             | Runs the interactive command-line interface                |

### Compatibility Layer

The editor attempts to import conversation classes from the main application but falls back to built-in minimal implementations if not available:

- `Node`: Represents a single message in a conversation
- `Tree`: Manages the tree structure of conversation nodes
- `Conversation`: Encapsulates a complete conversation with metadata

## Usage Guide

### Running the Editor

The editor can be launched from the command line:

```bash
# Launch with no file loaded
python conversation_editor.py

# Launch with a specific conversation file
python conversation_editor.py path/to/conversation.pickle

# Set version for a file without launching interactive mode
python conversation_editor.py path/to/conversation.pickle --set-version 1.1.0
```

### Interactive Commands

Once in interactive mode, the following commands are available:

| Command                 | Description                             | Example                                 |
| ----------------------- | --------------------------------------- | --------------------------------------- |
| `load <file>`           | Load a conversation pickle file         | `load conversations/abc123.pickle`      |
| `save [file]`           | Save the conversation                   | `save` or `save new_folder/`            |
| `view dir [path]`       | View all conversations in a directory   | `view dir` or `view dir conversations/` |
| `tree`                  | Print the conversation tree             | `tree`                                  |
| `branch`                | Print the current branch                | `branch`                                |
| `view [node_id]`        | View details of a node                  | `view` or `view abc123`                 |
| `cd <index>`            | Navigate to a child node by index       | `cd 0`                                  |
| `up`                    | Navigate to the parent node             | `up`                                    |
| `top`                   | Navigate to the root node               | `top`                                   |
| `edit`                  | Edit current node content               | `edit`                                  |
| `delete [node_id]`      | Delete a node                           | `delete` or `delete abc123`             |
| `prune`                 | Keep only current branch, delete others | `prune`                                 |
| `version <new_version>` | Set the conversation version            | `version 1.1.0`                         |
| `meta <key> <value>`    | Update conversation metadata            | `meta important true`                   |
| `quit`                  | Exit the program                        | `quit`                                  |

### Example Workflow

This example demonstrates how to load a conversation, navigate to a specific node, edit its content, and save the changes:

```
> load conversations/abc123.pickle
Loaded conversation: Chat about Python (v1.0.0)

> tree
Conversation: Chat about Python (v1.0.0)
ID: abc123-def456-ghi789
Latest timestamp: 2023-06-15 14:30:22

Tree structure:
  Root: 7a9b8c7... [2023-06-15 14:25:10]
    Human: 8def123... [2023-06-15 14:25:15]
      Content: How do I use dictionaries in Python?...
      AI: 9ghi456... [2023-06-15 14:25:20]
        Content: Dictionaries in Python are versatile data structures...
        Human: 0jkl789... [2023-06-15 14:30:10]
          Content: Can you show me an example of nested dictionaries?...
          → AI: 1mno012... [2023-06-15 14:30:22]
            Content: Here's an example of nested dictionaries:...

> cd 0
Navigated to: Human (0jkl789...)

> edit
Current content:
Can you show me an example of nested dictionaries?

Enter new content (type 'END' on a new line to finish):
Can you show me an example of nested dictionaries and how to access nested values?
END
Content updated

> save
Saved conversation to conversations/abc123.pickle
```

## Customization & Configuration

The Conversation Editor has minimal configuration but offers some flexibility:

### Command-Line Arguments

| Argument        | Description                                                         |
| --------------- | ------------------------------------------------------------------- |
| `file`          | Path to the conversation pickle file to edit                        |
| `--set-version` | Set conversation version and save without entering interactive mode |

### Import Behavior

The editor will first attempt to use the conversation classes from the main application. If these aren't available, it will use built-in minimal implementations with limited functionality. A message at startup indicates which behavior is active:

```
Using conversation classes from application
```

or

```
Using built-in conversation classes (limited functionality)
```

## Best Practices & Recommendations

### Data Management

1. **Always back up conversations** before making significant edits
2. **Use the `view dir` command** to check available conversations before loading
3. **Save frequently** when making multiple edits
4. **Be careful with the `prune` and `delete` commands** as they permanently remove data

### Efficient Navigation

1. Use `top` to reset to the root of the conversation
2. Use `branch` to see your current position in the tree
3. Combine `view` and `cd` to efficiently locate specific nodes
4. Use partial node IDs when using `view` or `delete` with a specific node

### Version Management

1. Keep versions consistent with `CONVERSATION_VERSION` in the main application
2. Use semantic versioning (x.y.z) format
3. Only increment major version (x) for incompatible changes
4. Only increment minor version (y) for new features

## Error Handling & Troubleshooting

### Common Issues

| Issue                       | Solution                                                                     |
| --------------------------- | ---------------------------------------------------------------------------- |
| `Error loading pickle file` | Ensure the file exists and is a valid conversation pickle                    |
| `No conversation loaded`    | Load a conversation with `load <file>` before using other commands           |
| `No current node`           | Use `top` to navigate to the root, then use `cd` to navigate to a valid node |
| `Invalid child index`       | Check available children with `view` before using `cd`                       |
| `Node not found`            | Ensure you're using a valid node ID or partial ID                            |

### Recovering from Errors

1. If the editor crashes, any unsaved changes will be lost
2. If navigation becomes confusing, use `top` to return to the root node and start over

## Additional Notes

### Integration with Local AI Chat

The Conversation Editor is designed to work with the conversation pickle files created by the Local AI Chat application. These files are typically stored in the `conversations` directory.

When the main application loads a conversation, it performs version compatibility checks. The editor respects and maintains these version attributes, allowing for proper backward compatibility.

### File Format

Conversation files use Python's pickle format with the following structure:

- `Conversation` object
  - `id`: UUID string
  - `name`: Conversation name
  - `tree`: Tree object with conversation structure
  - `metadata`: Dictionary of custom metadata
  - `latest_message_timestamp`: Datetime of most recent message
  - `version`: String in x.y.z format

### Related Files

- `conversation.py`: Defines the core conversation classes used by the main application
- `local-ai-chat-app.py`: The main application that creates and uses conversation files
