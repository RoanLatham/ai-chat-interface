import pickle
from datetime import datetime
from typing import List, Optional, Dict
import os
import uuid
import logging

# Node class represents a single message in the conversation
class Node:
    def __init__(self, content: str, sender: str, timestamp: datetime, model_name: Optional[str] = None):
        self.content = content
        self.sender = sender
        self.timestamp = timestamp
        self.children: List[Node] = []
        self.parent: Optional[Node] = None
        self.model_name: Optional[str] = model_name

# Tree class manages the branching structure of the conversation
class Tree:
    def __init__(self):
        self.root: Optional[Node] = None  # First message in the conversation
        self.current_node: Optional[Node] = None  # Currently active message

    # Add a new message to the conversation
    def add_node(self, content: str, sender: str, model_name: Optional[str] = None) -> Node:
        new_node = Node(content, sender, datetime.now(), model_name)
        if not self.root:
            self.root = new_node
        else:
            new_node.parent = self.current_node
            self.current_node.children.append(new_node)
        self.current_node = new_node
        return new_node

    # Edit an existing message, creating a new branch
    def edit_node(self, node: Node, new_content: str) -> Node:
        new_node = Node(new_content, node.sender, datetime.now())
        new_node.parent = node.parent
        if node.parent:
            node.parent.children.append(new_node)
        self.current_node = new_node
        return new_node

    # Move to a specific node in the conversation
    def navigate_to(self, node: Node):
        self.current_node = node

# Conversation class encapsulates the entire conversation structure
class Conversation:
    def __init__(self, name: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.tree = Tree()
        self.metadata: Dict[str, any] = {}  # For storing additional information
        self.latest_message_timestamp: Optional[datetime] = None

    # Add a new message to the conversation
    def add_message(self, content: str, sender: str, model_name: Optional[str] = None) -> Node:
        new_node = self.tree.add_node(content, sender, model_name)
        self.latest_message_timestamp = new_node.timestamp
        return new_node

    # Edit an existing message in the conversation
    def edit_message(self, node: Node, new_content: str) -> Node:
        new_node = self.tree.edit_node(node, new_content)
        self.latest_message_timestamp = new_node.timestamp
        return new_node

    # Navigate to a specific message in the conversation
    def navigate_to(self, node: Node):
        self.tree.navigate_to(node)

    # Get the current branch of the conversation (path from root to current node)
    def get_current_branch(self) -> List[Node]:
        branch = []
        current = self.tree.current_node
        while current:
            branch.append(current)
            current = current.parent
        return list(reversed(branch))

    # Save the conversation to a file
    def save(self, filename: str):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    # Load a conversation from a file
    @staticmethod
    def load(filename: str) -> 'Conversation':
        with open(filename, 'rb') as f:
            return pickle.load(f)
    
    def set_html_content(self, html: str):
        self.html_content = html

    def get_html_content(self) -> str:
        return self.html_content

# Utility function to list all saved conversations in a directory
def list_conversations(directory: str) -> Dict[str, str]:
    conversations = {}
    for f in os.listdir(directory):
        if f.endswith('.pickle'):
            conv = load_conversation(f[:-7], directory)
            try:
                name = conv.name
            except AttributeError:
                name = conv.id
                logging.warning(f"Conversation {conv.id} does not have a name attribute, using ID as name.")
            conversations[conv.id] = name
    # returns a ids as keys and names as values
    return conversations

# Create a new conversation with a given name
def create_conversation(name: str = "Naming...") -> Conversation:
    return Conversation(name)

# Save a conversation to a file in the specified directory
def save_conversation(conversation: Conversation, directory: str):
    filename = os.path.join(directory, f"{conversation.id}.pickle")
    conversation.save(filename)

# Load a conversation from a file in the specified directory
def load_conversation(id: str, directory: str) -> Conversation:
    filename = os.path.join(directory, f"{id}.pickle")
    return Conversation.load(filename)
