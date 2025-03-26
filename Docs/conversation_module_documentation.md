# Conversation Module Documentation

## Overview

The `conversation.py` module provides the core data structures and functionality for managing conversational interactions in the Local AI Chat application. It implements a tree-based conversation model that supports branching dialogues, allowing users to explore multiple conversation paths and maintain a complete history of interactions.

This module defines the fundamental classes for representing individual messages (`Node`), organizing them in a hierarchical structure (`Tree`), and encapsulating complete conversations with metadata (`Conversation`). It also provides utility functions for creating, loading, saving, and managing conversations.

A key feature of the conversation module is its versioning system, which ensures backward compatibility while allowing for future enhancements to the data structure.

## Features & Functionality

### Core Features

- **Tree-based Conversation Structure**: Supports branching dialogues with a hierarchical organization of messages
- **Message Context Preservation**: Maintains parent-child relationships between messages
- **Conversation Versioning**: Implements semantic versioning to handle compatibility across updates
- **Conversation Metadata**: Stores additional information about conversations (name, timestamp, custom fields)
- **Serialization**: Provides methods to save and load conversations from pickle files
- **Branch Navigation**: Supports traversing through different paths in a conversation

### Integration Points

The conversation module integrates with:

- **Local AI Chat Application (`local-ai-chat-app.py`)**: Provides the data structures that power the main application
- **Conversation Editor**: Serves as the data model for the developer tool that edits conversation files (see [Conversation Editor Documentation](GitIgnore/Docs/conversation_editor_documentation.md))
- **UI Components**: Supplies conversation data for display in the chat interface

## Key Components & Functions

### Class: `Node`

The `Node` class represents a single message in a conversation.

**Properties:**

| Property             | Type             | Description                                          |
| -------------------- | ---------------- | ---------------------------------------------------- |
| `id`                 | `str`            | Unique UUID for the node                             |
| `content`            | `str`            | The actual message content                           |
| `sender`             | `str`            | Who sent the message (e.g., "Human", "AI", "System") |
| `timestamp`          | `datetime`       | When the message was created                         |
| `children`           | `List[Node]`     | Child nodes (responses to this message)              |
| `parent`             | `Optional[Node]` | Parent node (message this is responding to)          |
| `model_name`         | `Optional[str]`  | Name of the AI model used (for AI messages)          |
| `internal_monologue` | `Optional[str]`  | AI's internal thought process (for AI messages)      |

### Class: `Tree`

The `Tree` class manages the branching structure of a conversation.

**Properties:**

| Property       | Type   | Description                               |
| -------------- | ------ | ----------------------------------------- |
| `root`         | `Node` | The root node of the tree                 |
| `current_node` | `Node` | Currently active node in the conversation |

**Methods:**

| Method               | Parameters                                                                                | Return Type      | Description                                                     |
| -------------------- | ----------------------------------------------------------------------------------------- | ---------------- | --------------------------------------------------------------- |
| `add_node`           | `content: str, sender: str, model_name: Optional[str], internal_monologue: Optional[str]` | `Node`           | Creates and adds a new message as a child of the current node   |
| `edit_node`          | `node_id: str, new_content: str`                                                          | `Optional[Node]` | Creates a new branch by editing an existing message             |
| `find_node`          | `node_id: str`                                                                            | `Optional[Node]` | Finds a node by its ID                                          |
| `get_siblings`       | `node_id: str`                                                                            | `List[Node]`     | Gets all nodes that share the same parent as the specified node |
| `get_current_branch` | None                                                                                      | `List[Node]`     | Gets all nodes from root to current node, in order              |
| `get_leaf_node`      | `node: Node`                                                                              | `Node`           | Finds the leaf node starting from the given node                |

### Class: `Conversation`

The `Conversation` class encapsulates a complete conversation with its tree structure and metadata.

**Properties:**

| Property                   | Type                 | Description                                        |
| -------------------------- | -------------------- | -------------------------------------------------- |
| `id`                       | `str`                | Unique UUID for the conversation                   |
| `name`                     | `str`                | User-friendly name of the conversation             |
| `tree`                     | `Tree`               | The conversation's tree structure                  |
| `metadata`                 | `Dict[str, Any]`     | Custom metadata for the conversation               |
| `latest_message_timestamp` | `Optional[datetime]` | When the most recent message was added             |
| `version`                  | `str`                | Version of the conversation format (e.g., "1.0.0") |

**Methods:**

| Method               | Parameters                                                                                | Return Type                                    | Description                                      |
| -------------------- | ----------------------------------------------------------------------------------------- | ---------------------------------------------- | ------------------------------------------------ |
| `add_message`        | `content: str, sender: str, model_name: Optional[str], internal_monologue: Optional[str]` | `Node`                                         | Adds a new message to the conversation           |
| `edit_message`       | `node_id: str, new_content: str`                                                          | `Optional[Node]`                               | Edits an existing message, creating a new branch |
| `get_current_branch` | None                                                                                      | `List[Node]`                                   | Gets current active branch of messages           |
| `get_siblings`       | `node_id: str`                                                                            | `List[Node]`                                   | Gets alternative messages at the same level      |
| `find_node`          | `node_id: str`                                                                            | `Optional[Node]`                               | Finds a specific message by ID                   |
| `navigate_to`        | `node_id: str`                                                                            | None                                           | Changes the active node                          |
| `save`               | `filename: str`                                                                           | None                                           | Saves the conversation to a file                 |
| `load` (static)      | `filename: str`                                                                           | `Tuple[Optional[Conversation], Optional[str]]` | Loads a conversation from a file                 |
| `set_name`           | `new_name: str`                                                                           | None                                           | Updates the conversation name                    |

### Utility Functions

| Function                 | Parameters                                   | Return Type                                    | Description                                 |
| ------------------------ | -------------------------------------------- | ---------------------------------------------- | ------------------------------------------- |
| `load_all_conversations` | `directory: str`                             | `List[Tuple[Conversation, Optional[str]]]`     | Loads all conversations from a directory    |
| `create_conversation`    | `name: str`                                  | `Conversation`                                 | Creates a new conversation                  |
| `save_conversation`      | `conversation: Conversation, directory: str` | None                                           | Saves a conversation to a directory         |
| `load_conversation`      | `id: str, directory: str`                    | `Tuple[Optional[Conversation], Optional[str]]` | Loads a conversation by ID from a directory |

## Versioning System

The conversation module implements a semantic versioning system to manage compatibility between different versions of conversations. For more details, see the [Conversation Versioning Documentation](GitIgnore/Docs/conversation_versioning.md).

The version format follows the `x.y.z` pattern where:

- `x`: Major version (incompatible changes)
- `y`: Minor version (backwards compatible changes)
- `z`: Patch version (bug fixes)

The current version is defined by the `CONVERSATION_VERSION` constant.

### Version Handling

When loading a conversation:

1. If the conversation's major version is lower than the current major version, the file is considered incompatible and is deleted
2. If the conversation's minor version is lower than the current minor version, a warning is generated but the conversation is loaded
3. The conversation's version is updated to the current version during saving

## Usage Guide

### Creating a New Conversation

```python
from conversation import create_conversation, save_conversation

# Create a new conversation with a name
new_conversation = create_conversation("Python Tutorial")

# Add messages to the conversation
human_msg = new_conversation.add_message("How do I use dictionaries in Python?", "Human")
ai_msg = new_conversation.add_message(
    "Dictionaries in Python are versatile data structures...",
    "AI",
    model_name="llama-3-8b",
    internal_monologue="I'll explain Python dictionaries with examples."
)

# Save the conversation to a directory
save_conversation(new_conversation, "conversations")
```

### Loading and Modifying a Conversation

```python
from conversation import load_conversation, save_conversation

# Load a conversation by ID
conversation, warning = load_conversation("abc123-def456-ghi789", "conversations")

if warning:
    print(f"Warning: {warning}")

if conversation:
    # Navigate to a specific node
    conversation.navigate_to("9ghi456")

    # Add a new message at the current position
    new_msg = conversation.add_message(
        "Can you show me an example of nested dictionaries?",
        "Human"
    )

    # Save the updated conversation
    save_conversation(conversation, "conversations")
```

### Working with Conversation Branches

```python
from conversation import load_conversation

# Load a conversation
conversation, _ = load_conversation("abc123-def456-ghi789", "conversations")

# Get the current branch
current_branch = conversation.get_current_branch()
for node in current_branch:
    print(f"{node.sender}: {node.content[:50]}...")

# Edit a message to create a new branch
edited_node = conversation.edit_message(
    "9ghi456",
    "Dictionaries in Python are key-value stores that allow fast lookups..."
)

# Navigate to the edited branch
conversation.navigate_to(edited_node.id)

# Get siblings (alternative branches) at a specific point
siblings = conversation.get_siblings("9ghi456")
for i, sibling in enumerate(siblings):
    print(f"Branch {i}: {sibling.content[:50]}...")
```

### Loading All Conversations

```python
from conversation import load_all_conversations

# Load all conversations from a directory
conversations = load_all_conversations("conversations")

# Process each conversation
for conversation, warning in conversations:
    print(f"Conversation: {conversation.name} (ID: {conversation.id})")
    if warning:
        print(f"Warning: {warning}")
    print(f"Messages: {len(conversation.get_current_branch())}")
    print()
```

## Best Practices & Recommendations

### Conversation Management

1. **Regularly Save Changes**: Call `save_conversation()` after making changes to prevent data loss
2. **Check Version Warnings**: Always check for warnings when loading conversations
3. **Use Meaningful Names**: Set descriptive conversation names to help with organization
4. **Preserve Context**: Keep conversation trees intact rather than flattening them

### Performance Considerations

1. **Limit Tree Size**: Very large conversation trees can impact performance
2. **Batch Operations**: When processing many conversations, batch your operations
3. **Consider Pruning**: Use the Conversation Editor's prune function for long-running conversations (see [Conversation Editor Documentation](GitIgnore/Docs/conversation_editor_documentation.md))

### Working with Branches

1. **Avoid Deep Nesting**: Extremely deep branches can be difficult to navigate
2. **Use Node IDs Carefully**: Store node IDs when you need to reference specific points in a conversation
3. **Check for Siblings**: Before navigating, check if there are alternative branches at the same level

## Error Handling & Troubleshooting

### Common Errors

| Error                             | Description                        | Resolution                                           |
| --------------------------------- | ---------------------------------- | ---------------------------------------------------- |
| `Error loading conversation: ...` | Failed to load a conversation file | Check if the file exists and is not corrupted        |
| `Error opening file`              | File permission issues             | Ensure you have proper permissions for the directory |
| `ValueError: Unsupported version` | Version incompatibility            | Use a compatible version of the application          |

### Handling Corrupted Files

If a conversation file becomes corrupted, you can:

1. Use the Conversation Editor to attempt recovery (see [Conversation Editor Documentation](GitIgnore/Docs/conversation_editor_documentation.md))
2. Check for backup files in the conversations directory
3. If the corruption is version-related, try using the `--set-version` command in the Conversation Editor

### Version Compatibility Issues

When encountering version warnings or errors:

1. For minor version differences (warnings), the conversation will load but might not support all features
2. For major version differences, the file will be automatically deleted to prevent data corruption
3. Always update to the latest version of the application to ensure compatibility

## Additional Notes

### Conversation Storage

Conversations are stored as pickle files in the designated conversations directory:

- In development mode: `<project_directory>/conversations/`
- In packaged mode: `<app_executable_directory>/conversations/`

Each file is named with the conversation's UUID and has a `.pickle` extension.

### Future Development

Future enhancements planned for the conversation module include:

1. Support for conversation tags and categorization
2. Enhanced metadata for conversation analytics
3. Export/import functionality for conversation migration
4. Performance optimizations for large conversation trees

### Related Files

- **Local AI Chat Application**: [local-ai-chat-app.py](local-ai-chat-app.py) - The main application that uses the conversation module
- **Conversation Editor**: [conversation_editor.py](conversation_editor.py) - A tool for manually editing conversation files
- **Conversation Editor Documentation**: [Conversation Editor Documentation](GitIgnore/Docs/conversation_editor_documentation.md) - Documentation for the conversation editor tool
- **Conversation Interface**: [chat-interface.html](chat-interface.html) - The web UI that displays conversations
