import pickle
from datetime import datetime
from typing import List, Optional, Dict
import os

# Node class represents a single message in the conversation
class Node:
    def __init__(self, content: str, sender: str, timestamp: datetime):
        self.content = content
        self.sender = sender
        self.timestamp = timestamp
        self.children: List[Node] = []  # List of reply messages
        self.parent: Optional[Node] = None  # Parent message, if any
        self.html_content: str = ""  # Chat container gui at time of the conversation being saved

# Tree class manages the branching structure of the conversation
class Tree:
    def __init__(self):
        self.root: Optional[Node] = None  # First message in the conversation
        self.current_node: Optional[Node] = None  # Currently active message

    # Add a new message to the conversation
    def add_node(self, content: str, sender: str) -> Node:
        new_node = Node(content, sender, datetime.now())
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
    def __init__(self, title: str):
        self.title = title
        self.tree = Tree()
        self.metadata: Dict[str, any] = {}  # For storing additional information

    # Add a new message to the conversation
    def add_message(self, content: str, sender: str) -> Node:
        return self.tree.add_node(content, sender)

    # Edit an existing message in the conversation
    def edit_message(self, node: Node, new_content: str) -> Node:
        return self.tree.edit_node(node, new_content)

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
        print(f"HTML content set to: {self.html_content}")

    def get_html_content(self) -> str:
        return self.html_content

# Utility function to list all saved conversations in a directory
def list_conversations(directory: str) -> List[str]:
    return [f[:-7] for f in os.listdir(directory) if f.endswith('.pickle')]

# Create a new conversation with a given title
def create_conversation(title: str) -> Conversation:
    return Conversation(title)

# Save a conversation to a file in the specified directory
def save_conversation(conversation: Conversation, directory: str):
    filename = os.path.join(directory, f"{conversation.title}.pickle")
    conversation.save(filename)

# Load a conversation from a file in the specified directory
def load_conversation(title: str, directory: str) -> Conversation:
    filename = os.path.join(directory, f"{title}.pickle")
    return Conversation.load(filename)
