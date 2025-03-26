# Conversation Versioning System

## Overview

The conversation versioning system implements a robust mechanism for maintaining compatibility between different versions of conversation files in the Local AI Chat application. It follows semantic versioning principles to ensure backward compatibility where possible while preventing data corruption from incompatible versions.

This system provides:

- Version tracking for all conversation files
- Automatic detection of version incompatibilities
- User notifications for potentially problematic conversation files
- Graceful handling of version differences
- Automated file management for incompatible versions

## Features & Functionality

### Semantic Versioning

The system uses a three-tier versioning format (`x.y.z`):

| Component | Name  | Purpose                         | Behavior on Mismatch             |
| --------- | ----- | ------------------------------- | -------------------------------- |
| x         | Major | Incompatible structural changes | Delete incompatible files        |
| y         | Minor | Backwards compatible features   | Display warnings, update version |
| z         | Patch | Bug fixes                       | No special handling              |

### Version Handling

- **Incompatible Versions**: When loading a conversation with an older major version than the current application, the file is automatically deleted to prevent data corruption.
- **Warning System**: When loading a conversation with an older minor version, a warning is displayed to the user while still loading the conversation.
- **Automatic Updates**: Conversations with older minor versions are automatically updated to the current version when loaded.
- **Version Display**: The current version of a conversation is displayed in the UI and CLI tools.

## Key Components & Functions

### Core Version Definition

```python
# From conversation.py
# Current version of the Conversation class
# x.y.z format where:
# x = major version (incompatible changes)
# y = minor version (backwards compatible changes)
# z = patch version (bug fixes)
CONVERSATION_VERSION = "1.0.0"
```

### Version Management Functions

#### Conversation Loading with Version Check

```python
@staticmethod
def load(filename: str) -> Tuple[Optional['Conversation'], Optional[str]]:
    try:
        with open(filename, 'rb') as f:
            conversation = pickle.load(f)

        # Check versioning
        if not hasattr(conversation, 'version'):
            # Handle legacy conversations without version
            conversation.version = "0.0.0"  # Consider as very old version

        # Parse versions for comparison
        current_parts = [int(p) for p in CONVERSATION_VERSION.split('.')]
        conv_parts = [int(p) for p in conversation.version.split('.')]

        # Major version difference - don't load at all
        if conv_parts[0] < current_parts[0]:
            os.remove(filename)  # Delete incompatible conversation file
            return None, f"Deleted incompatible conversation (v{conversation.version})"

        # Minor version difference - load but warn
        warning_message = None
        if conv_parts[1] < current_parts[1]:
            warning_message = f"This conversation was created with an older version (v{conversation.version}). Some features may not work as expected."
            # Update to current version
            conversation.version = CONVERSATION_VERSION

        return conversation, warning_message
    except Exception as e:
        logging.error(f"Error loading conversation: {str(e)}")
        return None, f"Error loading conversation: {str(e)}"
```

#### Version Validation in Current Conversation Route

```python
# From local-ai-chat-app.py
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
                # ... branch data ...
            ]
        })
    else:
        return jsonify({'conversation_id': None, 'conversation_name': None, 'branch': [], 'version_warning': None})
```

### Conversation Editor Tools

The conversation editor provides the ability to manually manage versions:

```
view dir [path]      - View all conversations in a directory (shows versions)
version <new_version> - Set the conversation version
```

## Usage Guide

### Handling Version Warnings in UI Code

When displaying conversations in the UI, check for version warnings:

```javascript
// Example of handling version warnings in UI code
function createConversationItem(conv) {
  const item = document.createElement("div");
  item.classList.add("conversation-item");

  // Add conversation name
  const title = document.createElement("span");
  title.textContent = conv.version_warning ? `${conv.name} ⚠️` : conv.name;

  // Show warning tooltip if needed
  if (conv.version_warning) {
    item.setAttribute("title", conv.version_warning);
    item.classList.add("warning");
  }

  return item;
}
```

### Implementing Version Checks

When updating the application with changes to the `Conversation` class, follow these steps:

1. **For backwards compatible changes**:

   - Increment the minor version (y) in `CONVERSATION_VERSION`
   - Ensure the application can handle conversations without the new features

2. **For incompatible changes**:

   - Increment the major version (x) in `CONVERSATION_VERSION`
   - Document that old conversation files will be deleted on load

3. **For bug fixes**:
   - Increment the patch version (z) in `CONVERSATION_VERSION`
   - No special handling is needed

## Best Practices & Recommendations

### When to Update Versions

- **Major Version (x)**: Increment when making structural changes to the `Conversation` or `Node` classes that would make old files incompatible or dangerous to load.
- **Minor Version (y)**: Increment when adding new attributes or features that older versions can safely ignore.
- **Patch Version (z)**: Increment for bug fixes or non-functional changes that don't affect file format.

### Migrating Between Versions

When implementing migration from an older version:

1. Check for missing attributes and provide defaults
2. Convert formats if needed
3. Mark the conversation as updated by setting its version to the current version

Example:

```python
# Example migration code
if conv_parts[1] < current_parts[1]:
    # Specific migrations for minor version changes
    if not hasattr(conversation, 'new_attribute'):
        conversation.new_attribute = default_value

    # Update to current version
    conversation.version = CONVERSATION_VERSION
```

### Testing Version Compatibility

When implementing version changes:

1. Create test conversations with the old version
2. Load them with the new version and verify warnings appear
3. Verify that incompatible files are properly deleted
4. Confirm that migrated files maintain their data integrity

## Error Handling & Troubleshooting

### Common Version-Related Errors

1. **Missing Conversations**

   - **Symptom**: Conversation files disappear after updating the application
   - **Cause**: Major version incompatibility triggered automatic deletion
   - **Solution**: Restore from backup if available, or implement a migration path instead of deletion

2. **Version Warnings**

   - **Symptom**: Warning icons appear next to conversation names
   - **Cause**: Minor version differences
   - **Solution**: Normal behavior, but implement proper migrations if features depend on new attributes

3. **Serialization Errors**
   - **Symptom**: Errors when loading conversations, typically `AttributeError`
   - **Cause**: Missing version-checking code or bugs in the versioning system
   - **Solution**: Fix the version-checking implementation, add try-except blocks for each attribute access

### Troubleshooting Steps

1. Check the file's version with the conversation editor:

   ```
   python conversation_editor.py path/to/file.pickle
   ```

2. Manually modify the version if needed (expert use only):

   ```
   > version 1.0.0
   > save
   ```

3. Export a conversation to JSON for inspection:
   ```
   > export conversation.json
   ```

## Additional Notes

The versioning system ensures smooth upgrades for users while protecting them from data corruption or unexpected behavior. When developing features that modify the conversation structure, always consider version compatibility and provide appropriate migrations for existing users.

### Related Files

- `conversation.py` - Core versioning logic
- `local-ai-chat-app.py` - UI version warnings and handling
- `conversation_editor.py` - Tools for managing versions manually

### Future Considerations

- Implementing version migration mechanisms for major version changes to avoid data loss
- Creating a version history file to track changes between versions
- Adding a backup system before attempting to load potentially incompatible files
