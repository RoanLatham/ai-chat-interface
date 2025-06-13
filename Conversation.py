import pickle
from datetime import datetime
from typing import List, Optional, Dict, Tuple
import os
import uuid
import logging

# Current version of the Conversation class
# x.y.z format where:
# x = major version (incompatible changes)
# y = minor version (backwards compatible changes)
# z = patch version (bug fixes)
CONVERSATION_VERSION = "1.0.0"

# Node class represents a single message in the conversation
class Node:
    def __init__(self, content: str, sender: str, timestamp: datetime, model_name: Optional[str] = None, internal_monologue: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.content = content
        self.sender = sender
        self.timestamp = timestamp
        self.children: List[Node] = []
        self.parent: Optional[Node] = None
        self.model_name: Optional[str] = model_name
        self.internal_monologue = internal_monologue

# Tree class manages the branching structure of the conversation
class Tree:
    def __init__(self):
        self.root = self.current_node = Node("", "Root", datetime.now()) # Empty root node, first message in brach is always child of root, to allow for multiple branches including the first message in a conversation 

    # Add a new message to the conversation
    def add_node(self, content: str, sender: str, model_name: Optional[str] = None, internal_monologue: Optional[str] = None) -> Node:
        new_node = Node(content, sender, datetime.now(), model_name, internal_monologue)
        new_node.parent = self.current_node
        self.current_node.children.append(new_node)
        self.current_node = new_node
        return new_node
    
    # Edit an existing message, creating a new branch
    def edit_node(self, node_id: str, new_content: str) -> Optional[Node]:
        node = self.find_node(node_id)
        if node and node != self.root:
            # Don't preserve planning when editing (set to None)
            new_node = Node(new_content, node.sender, datetime.now(), node.model_name, None)
            new_node.parent = node.parent
            node.parent.children.append(new_node)
            self.current_node = new_node
            return new_node
        return None
    
    # Find a specific node in the conversation
    def find_node(self, node_id: str) -> Optional[Node]:
        def dfs(node):
            if node.id == node_id:
                return node
            for child in node.children:
                result = dfs(child)
                if result:
                    return result
            return None
        return dfs(self.root) if self.root else None

    def get_siblings(self, node_id: str) -> List[Node]:
        node = self.find_node(node_id)
        if node and node.parent and node != self.root:
            siblings = sorted(node.parent.children, key=lambda x: x.timestamp)
            return siblings
        else:
            return []

    def get_current_branch(self) -> List[Node]:
        branch = []
        current = self.current_node
        while current and current != self.root:
            branch.append(current)
            current = current.parent
        return list(reversed(branch))
    
    def get_leaf_node(self, node):
        while node.children:
            node = node.children[0]
        return node

# Conversation class encapsulates the entire conversation structure
class Conversation:
    def __init__(self, name: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.tree = Tree()
        self.metadata: Dict[str, any] = {}  # For storing additional information
        self.latest_message_timestamp: Optional[datetime] = None
        self.version = CONVERSATION_VERSION  # Store the current version when created

    # Add a new message to the conversation
    def add_message(self, content: str, sender: str, model_name: Optional[str] = None, internal_monologue: Optional[str] = None) -> Node:
        new_node = self.tree.add_node(content, sender, model_name, internal_monologue)
        self.latest_message_timestamp = new_node.timestamp
        return new_node

    # Edit an existing message in the conversation
    def edit_message(self, node_id: str, new_content: str) -> Optional[Node]:
        return self.tree.edit_node(node_id, new_content)

    # Get the current branch of the conversation (path from root to current node)
    def get_current_branch(self) -> List[Node]:
        return self.tree.get_current_branch()

    # Get the siblings of a specific message in the conversation from its ID
    def get_siblings(self, node_id: str) -> List[Node]:
        return self.tree.get_siblings(node_id)

    # Find a specific message in the conversation from its ID
    def find_node(self, node_id: str) -> Optional[Node]:
        node = self.tree.find_node(node_id)
        return node if node != self.tree.root else None

    # Navigate to a specific message in the conversation
    def navigate_to(self, node_id: str):
        node = self.tree.find_node(node_id)
        if node:
            self.tree.current_node = node

    # Save the conversation to a file
    def save(self, filename: str):
        self.version = CONVERSATION_VERSION
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    # Load a conversation from a file
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
    
    def set_html_content(self, html: str):
        self.html_content = html

    def get_html_content(self) -> str:
        return self.html_content
    
    def set_name(self, new_name: str):
        self.name = new_name

def load_all_conversations(directory: str) -> List[Tuple[Conversation, Optional[str]]]:
    conversations = []
    for f in os.listdir(directory):
        if f.endswith('.pickle'):
            try:
                conv, warning = load_conversation(f[:-7], directory)
                if conv:
                    conversations.append((conv, warning))
            except Exception as e:
                logging.error(f"Error loading conversation {f}: {str(e)}")
    return sorted(conversations, key=lambda x: x[0].latest_message_timestamp or datetime.min, reverse=True)

# Create a new conversation with a given name
def create_conversation(name: str = "Unnamed Conversation") -> Conversation:
    return Conversation(name)

# Save a conversation to a file in the specified directory
def save_conversation(conversation: Conversation, directory: str):
    filename = os.path.join(directory, f"{conversation.id}.pickle")
    conversation.save(filename)

# Load a conversation from a file in the specified directory
def load_conversation(id: str, directory: str) -> Tuple[Optional[Conversation], Optional[str]]:
    filename = os.path.join(directory, f"{id}.pickle")
    return Conversation.load(filename)
