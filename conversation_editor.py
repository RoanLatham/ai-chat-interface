"""
Conversation Editor - A development tool for manually editing conversation .pickle files.

Features:
- Load and view conversation pickle files
- Traverse through conversation nodes
- Edit conversation content and metadata
- Delete nodes from the conversation tree
- Set/update conversation version

"""

import os
import sys
import pickle
import json
import argparse
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

# Try importing from the current directory first
try:
    from conversation import Conversation, Node, Tree, CONVERSATION_VERSION
    IMPORTED_FROM_APP = True
except ImportError:
    IMPORTED_FROM_APP = False
    # Define minimal classes for standalone use
    CONVERSATION_VERSION = "1.0.0"  # Default version if not imported
    
    class Node:
        def __init__(self, content: str, sender: str, timestamp: datetime, 
                    model_name: Optional[str] = None, internal_monologue: Optional[str] = None):
            self.id = str(uuid.uuid4())
            self.content = content
            self.sender = sender
            self.timestamp = timestamp
            self.children = []
            self.parent = None
            self.model_name = model_name
            self.internal_monologue = internal_monologue
    
    class Tree:
        def __init__(self):
            self.root = self.current_node = Node("", "Root", datetime.now())
            
        def get_current_branch(self):
            branch = []
            current = self.current_node
            while current and current != self.root:
                branch.append(current)
                current = current.parent
            return list(reversed(branch))
    
    class Conversation:
        def __init__(self, name: str):
            self.id = str(uuid.uuid4())
            self.name = name
            self.tree = Tree()
            self.metadata = {}
            self.latest_message_timestamp = None
            self.version = CONVERSATION_VERSION

class ConversationEditor:
    def __init__(self):
        self.conversation = None
        self.current_node = None
        self.file_path = None
        self.modified = False
    
    def load_pickle(self, file_path: str) -> bool:
        """Load a conversation pickle file"""
        try:
            with open(file_path, 'rb') as f:
                self.conversation = pickle.load(f)
                self.file_path = file_path
                self.current_node = self.conversation.tree.current_node
                print(f"Loaded conversation: {self.conversation.name} (v{self.conversation.version})")
                return True
        except Exception as e:
            print(f"Error loading pickle file: {e}")
            return False
    
    def save_pickle(self, file_path: Optional[str] = None) -> bool:
        """Save the conversation to a pickle file"""
        if not self.conversation:
            print("No conversation loaded")
            return False
        
        # If no path provided, use the original file path's directory
        if not file_path:
            if not self.file_path:
                print("No file path specified and no original file path available")
                return False
            # Use the directory from the original file path
            file_path = os.path.dirname(self.file_path)
        
        # If the path is a directory, append the ID as filename
        if os.path.isdir(file_path) or not file_path.endswith('.pickle'):
            # Regenerate ID if saving to a new location
            if file_path != os.path.dirname(self.file_path or ''):
                self.regenerate_id()
            
            # Ensure path ends with separator if it's a directory
            if not file_path.endswith(os.sep) and os.path.isdir(file_path):
                file_path = file_path + os.sep
                
            # Create the full path with ID as filename
            file_path = os.path.join(file_path, f"{self.conversation.id}.pickle")
        else:
            # If it's a complete file path with .pickle extension
            # Extract just the directory and use conversation ID as filename
            dir_path = os.path.dirname(file_path)
            # Regenerate ID if saving to a new location
            if dir_path != os.path.dirname(self.file_path or ''):
                self.regenerate_id()
            file_path = os.path.join(dir_path, f"{self.conversation.id}.pickle")
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'wb') as f:
                pickle.dump(self.conversation, f)
            
            self.file_path = file_path
            print(f"Saved conversation to {file_path}")
            self.modified = False
            return True
        except Exception as e:
            print(f"Error saving pickle file: {e}")
            return False
    
    def regenerate_id(self) -> None:
        """Regenerate the conversation ID"""
        if not self.conversation:
            return
        
        old_id = self.conversation.id
        self.conversation.id = str(uuid.uuid4())
        print(f"Regenerated conversation ID: {old_id} → {self.conversation.id}")
        self.modified = True
    
    def print_node(self, node: Node, level: int = 0, i_in_branch: int =0) -> None:
        """Print a node and its details"""
        current_marker = "→ " if node == self.current_node else "  "
        indent = "  " * level
        sender_color = {
            "Human": "\033[94m",  # Blue
            "AI": "\033[92m",     # Green
            "System": "\033[93m", # Yellow
            "Root": "\033[90m"    # Gray
        }.get(node.sender, "\033[0m")
        
        print(indent + (f"{i_in_branch} " if i_in_branch != 0 else "  ") + ( "-" *40) )
        print(f"{indent}{current_marker}{sender_color}{node.sender}\033[0m: {node.id[:8]}... [{node.timestamp.strftime('%Y-%m-%d %H:%M:%S')}]")
        if node.content:
            max_content = 50
            content_preview = node.content[:max_content] + ("..." if len(node.content) > max_content else "")
            print(f"{indent}  Content: {content_preview}")
        if node.model_name:
            print(f"{indent}  Model: {node.model_name}")
        print(indent + "  " +( "-" *40) )
    
    def print_tree(self, node: Optional[Node] = None, level: int = 0) -> None:
        """Print the conversation tree"""
        if not self.conversation:
            print("No conversation loaded")
            return
        
        if node is None:
            node = self.conversation.tree.root
            print(f"Conversation: {self.conversation.name} (v{self.conversation.version})")
            print(f"ID: {self.conversation.id}")
            print(f"Latest timestamp: {self.conversation.latest_message_timestamp}")
            print("\nTree structure:")
        
        self.print_node(node, level)
        # print("\n")
        
        for child in node.children:
            self.print_tree(child, level + 1)
    
    def view_node(self, node_id: Optional[str] = None) -> None:
        """View detailed information about a node"""
        if not self.conversation:
            print("No conversation loaded")
            return
        
        target_node = None
        if node_id:
            # Find the specified node
            target_node = self.find_node_by_id(node_id)
            if not target_node:
                print(f"Node with ID {node_id} not found")
                return
        else:
            # Use current node
            target_node = self.current_node
            if not target_node:
                print("No current node")
                return
        
        # Print all node details
        print("\n" + "=" * 50)
        print(f"NODE DETAILS: {target_node.id}")
        print("=" * 50)
        print(f"Sender: {target_node.sender}")
        print(f"Timestamp: {target_node.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if target_node.model_name:
            print(f"Model: {target_node.model_name}")
        
        print(f"Parent: {target_node.parent.id[:8]}... ({target_node.parent.sender})" if target_node.parent else "Parent: None")
        
        if target_node.children:
            print("\nChildren:")
            for i, child in enumerate(target_node.children):
                print(f"  {i}. {child.id[:8]}... ({child.sender})")
        else:
            print("\nChildren: None")

        if hasattr(target_node, "internal_monologue") and target_node.internal_monologue:
            print("\nInternal Monologue:")
            print("~" * 50)
            print(target_node.internal_monologue)
            print("~" * 50)
        
        print("\nContent:")
        print("-" * 50)
        print(target_node.content or "(empty)")
        print("-" * 50)

    
    def find_node_by_id(self, node_id: str) -> Optional[Node]:
        """Find a node by its ID"""
        def search(node):
            if node.id.startswith(node_id) or node.id == node_id:
                return node
            for child in node.children:
                result = search(child)
                if result:
                    return result
            return None
        
        return search(self.conversation.tree.root)
    
    def print_branch(self) -> None:
        """Print the current branch from root to current node"""
        if not self.conversation:
            print("No conversation loaded")
            return
        
        branch = []
        current = self.current_node
        while current:
            branch.append(current)
            current = current.parent
        
        branch.reverse()
        
        print("\nCurrent branch (root to current):")
        for i, node in enumerate(branch):
            if node != self.conversation.tree.root:  # Skip root node
                # print(f"{i}. ", end="")
                self.print_node(node, i_in_branch=i)
    
    def set_version(self, new_version: str) -> None:
        """Set the conversation version"""
        if not self.conversation:
            print("No conversation loaded")
            return
        
        old_version = self.conversation.version
        self.conversation.version = new_version
        print(f"Updated version: {old_version} → {new_version}")
        self.modified = True
    
    def navigate_to_child(self, index: int) -> None:
        """Navigate to a child node by index"""
        if not self.current_node:
            print("No current node")
            return
        
        if index < 0 or index >= len(self.current_node.children):
            print(f"Invalid child index. Valid range: 0-{len(self.current_node.children)-1}")
            return
        
        self.current_node = self.current_node.children[index]
        print(f"Navigated to: {self.current_node.sender} ({self.current_node.id[:8]}...)")
    
    def navigate_to_parent(self) -> None:
        """Navigate to the parent node"""
        if not self.current_node or not self.current_node.parent:
            print("No parent node available")
            return
        
        self.current_node = self.current_node.parent
        print(f"Navigated to parent: {self.current_node.sender} ({self.current_node.id[:8]}...)")
    
    def edit_node_content(self, content: str) -> None:
        """Edit the content of the current node"""
        if not self.current_node:
            print("No current node")
            return
        
        old_content = self.current_node.content
        self.current_node.content = content
        print("Content updated")
        self.modified = True
    
    def delete_node(self, node_id: str = None) -> None:
        """Delete a node (and its children) from the conversation"""
        if not self.conversation:
            print("No conversation loaded")
            return
        
        target_id = node_id or (self.current_node.id if self.current_node else None)
        if not target_id:
            print("No node specified to delete")
            return
        
        # Skip root node deletion
        if target_id == self.conversation.tree.root.id:
            print("Cannot delete the root node")
            return
        
        # Find the node and its parent
        def find_node_and_parent(node, target_id):
            if node.id == target_id:
                return node, node.parent
            
            for child in node.children:
                result = find_node_and_parent(child, target_id)
                if result[0]:
                    return result
            
            return None, None
        
        node, parent = find_node_and_parent(self.conversation.tree.root, target_id)
        
        if not node or not parent:
            print(f"Node {target_id} not found")
            return
        
        # Remove node from parent's children
        parent.children = [child for child in parent.children if child.id != target_id]
        
        # Update current node if needed
        if self.current_node and self.current_node.id == target_id:
            self.current_node = parent
            self.conversation.tree.current_node = parent
        
        print(f"Deleted node {target_id[:8]}... and its children")
        self.modified = True
    
    def update_metadata(self, key: str, value: Any) -> None:
        """Update conversation metadata"""
        if not self.conversation:
            print("No conversation loaded")
            return
        
        self.conversation.metadata[key] = value
        print(f"Updated metadata: {key} = {value}")
        self.modified = True
    
    def prune_to_current_branch(self) -> None:
        """Keep only the current branch and delete all other branches"""
        if not self.conversation or not self.current_node:
            print("No conversation or current node")
            return
        
        # Get the current branch as a list of nodes
        branch = []
        current = self.current_node
        while current:
            branch.append(current)
            current = current.parent
        
        # Reverse to get root-to-current order
        branch.reverse()
        
        # Now prune the tree - for each node in the branch,
        # keep only the child that's also in the branch
        deleted_count = 0
        for i, node in enumerate(branch[:-1]):  # Skip the last node (current)
            next_in_branch = branch[i+1]
            
            # Keep track of how many children we'll delete
            deleted_count += len(node.children) - 1
            
            # Replace children with just the one in our branch
            node.children = [child for child in node.children if child == next_in_branch]
        
        print(f"Pruned conversation: removed {deleted_count} branches")
        print("Only the current branch remains")
        self.modified = True
    
    def view_directory(self, directory_path: Optional[str] = None) -> None:
        """View basic information about all conversation pickle files in a directory"""
        # Use provided directory or try to find a default conversations directory
        if not directory_path:
            # Check for common conversation directories
            common_dirs = [
                "conversations",
                os.path.join(os.getcwd(), "conversations"),
                os.path.join(os.path.dirname(os.getcwd()), "conversations")
            ]
            
            for dir_path in common_dirs:
                if os.path.exists(dir_path) and os.path.isdir(dir_path):
                    directory_path = dir_path
                    break
        
        if not directory_path or not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            print("Error: Valid directory path not provided or found")
            return
        
        print(f"\nScanning directory: {directory_path}")
        print("=" * 70)
        print(f"{'NAME':<30}\n{'ID':<36}\n{'VERSION':<10}\n{'LAST UPDATED':<20}")
        print("=" * 70)
        
        conversation_files = [f for f in os.listdir(directory_path) if f.endswith('.pickle')]
        
        if not conversation_files:
            print("No conversation files found in this directory.")
            return
        
        # Track conversations for sorting
        conversation_data = []
        
        # Process each file
        for file_name in conversation_files:
            file_path = os.path.join(directory_path, file_name)
            try:
                # Try to load just enough to get basic info
                with open(file_path, 'rb') as f:
                    conversation = pickle.load(f)
                
                # Extract basic information
                name = getattr(conversation, 'name', 'Unknown')
                id_value = getattr(conversation, 'id', file_name.replace('.pickle', ''))
                version = getattr(conversation, 'version', 'Unknown')
                
                # Get timestamp
                timestamp = getattr(conversation, 'latest_message_timestamp', None)
                if not timestamp:
                    # Try to get file modification time as fallback
                    timestamp = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                conversation_data.append({
                    'name': name,
                    'id': id_value,
                    'version': version,
                    'timestamp': timestamp,
                    'file_name': file_name
                })
                
            except Exception as e:
                print(f"Error loading {file_name}: {e}")
        
        # Sort by timestamp (newest first)
        conversation_data.sort(key=lambda x: x['timestamp'] if x['timestamp'] else datetime.min, reverse=True)
        
        # Display the conversations
        for i, data in enumerate(conversation_data):
            timestamp_str = data['timestamp'].strftime('%Y-%m-%d %H:%M') if data['timestamp'] else 'Unknown'
            id_str = str(data['id'])[:34] + '..' if len(str(data['id'])) > 36 else str(data['id'])
            print(f"-" * 70)
            print(f"{i+1}\n{data['name']:<28}\n{id_str:<36}\n{data['version']:<10}\n{timestamp_str:<20}")
            print("-" * 70 + "\n")
        
        print(f"\nFound {len(conversation_data)} conversation files")
    
    def interactive_mode(self) -> None:
        """Run an interactive CLI session"""
        while True:
            if self.conversation:
                status = f"[{'Modified' if self.modified else 'Saved'}]"
                print(f"\n{status} Conversation: {self.conversation.name} (v{self.conversation.version})")
                if self.current_node:
                    node_type = "Root" if self.current_node == self.conversation.tree.root else self.current_node.sender
                    print(f"Current node: {node_type} ({self.current_node.id[:8]}...)")
                    if self.current_node.children:
                        print(f"Children: {len(self.current_node.children)}")
            
            print("\nAvailable commands:")
            print("  load <file>          - Load a conversation pickle file")
            print("  save [file]          - Save the conversation")
            print("  view dir [path]      - View all conversations in a directory")
            print(" ")
            print("  tree                 - Print the conversation tree")
            print("  branch               - Print the current branch")
            print("  view [node_id]       - View details of current node or specified node")
            print("  cd <index>           - Navigate to a child node by index")
            print("  up                   - Navigate to the parent node")
            print("  top                  - Navigate to the root node")
            print(" ")
            print("  edit                 - Edit current node content")
            print("  delete [node_id]     - Delete current node or specified node")
            print("  prune                - Keep only the current branch, delete all others")
            print("  version <new_version> - Set the conversation version")
            print(" ")
            print("  meta <key> <value>   - Update conversation metadata")
            print("  quit                 - Exit the program")
            
            cmd = input("\n> ").strip().split(maxsplit=2)  # Allow for "view dir [path]" with spaces
            command = cmd[0].lower() if cmd else ""
            
            if command == "quit" or command == "exit":
                if self.modified:
                    save = input("Save changes before quitting? (y/n): ").lower()
                    if save == 'y':
                        self.save_pickle()
                break
            
            elif command == "load":
                if len(cmd) < 2:
                    print("Usage: load <file>")
                    continue
                
                if self.modified:
                    save = input("Save current conversation before loading? (y/n): ").lower()
                    if save == 'y':
                        self.save_pickle()
                
                self.load_pickle(cmd[1])
                
            elif command == "save":
                save_path = cmd[1] if len(cmd) > 1 else self.file_path
                self.save_pickle(save_path)
                
            elif command == "tree":
                self.print_tree()
                
            elif command == "branch":
                self.print_branch()
                
            elif command == "view":
                if len(cmd) > 1 and cmd[1].lower() == "dir":
                    # Handle "view dir [path]" command
                    dir_path = cmd[2] if len(cmd) > 2 else None
                    self.view_directory(dir_path)
                else:
                    # Original view command
                    node_id = cmd[1] if len(cmd) > 1 else None
                    self.view_node(node_id)
                
            elif command == "cd":
                if len(cmd) < 2:
                    print("Usage: cd <index>")
                    continue
                
                try:
                    index = int(cmd[1])
                    self.navigate_to_child(index)
                except ValueError:
                    print("Usage: cd <index>")
                
            elif command == "up":
                self.navigate_to_parent()
                
            elif command == "top":
                if self.conversation:
                    self.current_node = self.conversation.tree.root
                    print("Navigated to root node")
                    
            elif command == "edit":
                if not self.current_node:
                    print("No current node to edit")
                    continue
                    
                print(f"Current content:\n{self.current_node.content}")
                print("\nEnter new content (type 'END' on a new line to finish):")
                
                content_lines = []
                while True:
                    line = input()
                    if line == "END":
                        break
                    content_lines.append(line)
                
                new_content = "\n".join(content_lines)
                self.edit_node_content(new_content)
                
            elif command == "delete":
                node_id = cmd[1] if len(cmd) > 1 else (self.current_node.id if self.current_node else None)
                self.delete_node(node_id)
                
            elif command == "prune":
                confirmation = input("This will delete all nodes except those on the current branch. Continue? (y/n): ").lower()
                if confirmation == 'y':
                    self.prune_to_current_branch()
                
            elif command == "version":
                if len(cmd) < 2:
                    print("Usage: version <new_version>")
                    continue
                
                self.set_version(cmd[1])
                
            elif command == "meta":
                if len(cmd) < 3:
                    print("Usage: meta <key> <value>")
                    continue
                
                key, value = cmd[1], cmd[2]
                # Try to convert value to appropriate type
                try:
                    # Try to convert to number or boolean
                    if value.lower() == "true":
                        value = True
                    elif value.lower() == "false":
                        value = False
                    elif value.isdigit():
                        value = int(value)
                    elif value.replace(".", "", 1).isdigit():
                        value = float(value)
                except:
                    pass  # Keep as string
                
                self.update_metadata(key, value)
                
            else:
                print(f"Unknown command: {command}")

def main():
    parser = argparse.ArgumentParser(description="Conversation Pickle Editor")
    parser.add_argument("file", nargs="?", help="Conversation pickle file to edit")
    parser.add_argument("--batch", help="Run batch commands from file")
    parser.add_argument("--version", action="version", version=f"Conversation Pickle Editor v1.0.0")
    
    # Special operations
    parser.add_argument("--set-version", help="Set conversation version and save")
    
    args = parser.parse_args()
    
    editor = ConversationEditor()
    
    # Handle special operations
    if args.file and args.set_version:
        if editor.load_pickle(args.file):
            editor.set_version(args.set_version)
            editor.save_pickle()
        return
    
    # Normal interactive mode
    if args.file:
        editor.load_pickle(args.file)
    
    if args.batch:
        print("Batch mode not implemented yet")
        return
    
    # Show info about import source
    if IMPORTED_FROM_APP:
        print("Using conversation classes from application")
    else:
        print("Using built-in conversation classes (limited functionality)")
    
    try:
        editor.interactive_mode()
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()