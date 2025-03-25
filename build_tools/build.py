"""
Build script for Local AI Chat App
This script packages the Local AI Chat application into a standalone executable
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse

# Get the root directory (parent of build_tools)
def get_root_dir():
    """Get the root directory of the project"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Get paths relative to root directory
def get_path(relative_path):
    """Get absolute path from path relative to project root"""
    return os.path.join(get_root_dir(), relative_path)

def ensure_dependencies():
    """Ensure all dependencies are installed"""
    print("Checking and installing required dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # These are the main dependencies for our application
    required_packages = [
        "pyinstaller",
        "flask",
        "llama-cpp-python",
        "dataclasses"
    ]
    
    for package in required_packages:
        print(f"Ensuring {package} is installed...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("All dependencies installed successfully!")

def clean_build_directories():
    """Clean build and dist directories"""
    print("Cleaning build directories...")
    root_dir = get_root_dir()
    dirs_to_clean = [
        os.path.join(root_dir, 'build'), 
        os.path.join(root_dir, 'dist'), 
        os.path.join(root_dir, 'Local_AI_Chat.spec')
    ]
    
    for dir_to_clean in dirs_to_clean:
        if os.path.exists(dir_to_clean):
            if os.path.isdir(dir_to_clean):
                shutil.rmtree(dir_to_clean)
            else:
                os.remove(dir_to_clean)
    
    print("Build directories cleaned successfully!")

def create_build_directories():
    """Create necessary directories for the build"""
    print("Creating build directories...")
    root_dir = get_root_dir()
    os.makedirs(os.path.join(root_dir, "dist"), exist_ok=True)
    os.makedirs(os.path.join(root_dir, "build"), exist_ok=True)
    
    print("Build directories created successfully!")

def create_user_data_directories():
    """Create user data directories and placeholder files (after PyInstaller build)"""
    print("Creating user data directories...")
    root_dir = get_root_dir()
    output_dir = os.path.join(root_dir, "dist", "LocalAIChat")
    
    # Create ai_models directory with placeholder file
    ai_models_dir = os.path.join(output_dir, "ai_models")
    os.makedirs(ai_models_dir, exist_ok=True)
    placeholder_file = os.path.join(ai_models_dir, "Place AI model gguf files here")
    with open(placeholder_file, 'w') as f:
        f.write("Place your GGUF model files in this directory.\n")
        f.write("The application will detect them when it starts.\n")
    
    # Copy example_conversations directory if it exists, otherwise create empty conversations directory
    example_conversations_dir = os.path.join(root_dir, "example_conversations")
    conversations_dir = os.path.join(output_dir, "conversations")
    
    if os.path.exists(example_conversations_dir) and os.path.isdir(example_conversations_dir):
        print(f"Copying example conversations from {example_conversations_dir}")
        if os.path.exists(conversations_dir):
            shutil.rmtree(conversations_dir)
        shutil.copytree(example_conversations_dir, conversations_dir)
    else:
        print("Example conversations directory not found, creating empty conversations directory")
        os.makedirs(conversations_dir, exist_ok=True)
    
    # Create logs directory
    os.makedirs(os.path.join(output_dir, "logs"), exist_ok=True)
    
    print("User data directories created successfully!")

def copy_resources():
    """Copy necessary resource files to the build directory"""
    print("Copying resource files...")
    root_dir = get_root_dir()
    output_dir = os.path.join(root_dir, "dist", "LocalAIChat")
    
    # Copy the system prompt file
    shutil.copy(os.path.join(root_dir, "system-prompt.txt"), output_dir)
    
    # Copy the README file if it exists
    if os.path.exists(os.path.join(root_dir, "README.md")):
        shutil.copy(os.path.join(root_dir, "README.md"), output_dir)
    
    # Copy icon directory if it exists
    if os.path.exists(os.path.join(root_dir, "icon")):
        icon_output_dir = os.path.join(output_dir, "icon")
        os.makedirs(icon_output_dir, exist_ok=True)
        for file in os.listdir(os.path.join(root_dir, "icon")):
            if os.path.isfile(os.path.join(root_dir, "icon", file)):
                shutil.copy(os.path.join(root_dir, "icon", file), icon_output_dir)
    
    print("Resource files copied successfully!")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable with PyInstaller...")
    root_dir = get_root_dir()
    
    # Check if we have a spec file
    spec_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "LocalAIChat.spec")
    if os.path.exists(spec_file):
        print("Using existing spec file for build...")
        subprocess.check_call(["pyinstaller", spec_file, "--clean", "--noconfirm"])
        print("Executable built successfully!")
        return
    
    # If no spec file, use the command line arguments approach
    # Define PyInstaller command
    pyinstaller_args = [
        "pyinstaller",
        "--name=LocalAIChat",
        "--onedir",
        "--console",  # Show console window
        "--noconfirm",  # Skip confirmation prompts
        "--clean",
        "--additional-hooks-dir=.",  # Look for hook-llama in the current directory
        f"--add-data={os.path.join(root_dir, 'system-prompt.txt')}{os.pathsep}.",
        f"--add-data={os.path.join(root_dir, 'chat-interface.html')}{os.pathsep}.",
        f"--add-data={os.path.join(root_dir, 'conversation.py')}{os.pathsep}.",
    ]
    
    # Add icon directory if it exists
    if os.path.exists(os.path.join(root_dir, "icon")):
        pyinstaller_args.append(f"--add-data={os.path.join(root_dir, 'icon')}{os.pathsep}icon")
    
    # Add Windows icon if it exists
    if platform.system() == "Windows":
        if os.path.exists(os.path.join(root_dir, "icon/AII-console-icon.ico")):
            pyinstaller_args.append(f"--icon={os.path.join(root_dir, 'icon/AII-console-icon.ico')}")
        elif os.path.exists(os.path.join(root_dir, "icon/AII-icon.ico")):
            pyinstaller_args.append(f"--icon={os.path.join(root_dir, 'icon/AII-icon.ico')}")
    
    # Add the main script
    pyinstaller_args.append(os.path.join(root_dir, "local-ai-chat-app.py"))
    
    # Run PyInstaller
    subprocess.check_call(pyinstaller_args)
    
    print("Executable built successfully!")

def create_launcher():
    """Create a launcher script/batch file for easy startup"""
    print("Creating launcher script...")
    root_dir = get_root_dir()
    output_dir = os.path.join(root_dir, "dist", "LocalAIChat")
    
    if platform.system() == "Windows":
        # Create a batch file launcher for Windows
        launcher_path = os.path.join(output_dir, "Launch_LocalAIChat.bat")
        with open(launcher_path, "w") as f:
            f.write('@echo off\n')
            f.write('echo Starting Local AI Chat Application...\n')
            f.write('start "" "%~dp0LocalAIChat.exe"\n')
        
        # Make the launcher executable
        os.chmod(launcher_path, 0o755)
    else:
        # Create a shell script launcher for macOS/Linux
        launcher_path = os.path.join(output_dir, "Launch_LocalAIChat.sh")
        with open(launcher_path, "w") as f:
            f.write('#!/bin/bash\n')
            f.write('echo "Starting Local AI Chat Application..."\n')
            f.write('cd "$(dirname "$0")"\n')
            f.write('./LocalAIChat\n')
        
        # Make the launcher executable
        os.chmod(launcher_path, 0o755)
    
    print(f"Launcher script created at: {launcher_path}")

def create_readme():
    """Create a README file for the packaged application"""
    print("Creating README file...")
    root_dir = get_root_dir()
    output_dir = os.path.join(root_dir, "dist", "LocalAIChat")
    readme_path = os.path.join(output_dir, "README.txt")
    
    with open(readme_path, "w") as f:
        f.write("Local AI Chat Application\n")
        f.write("========================\n\n")
        f.write("Thank you for installing the Local AI Chat application!\n\n")
        f.write("Getting Started:\n")
        f.write("1. Launch the application using the Launch_LocalAIChat file.\n")
        f.write("2. Place your GGUF model files in the 'ai_models' folder.\n")
        f.write("Folders:\n")
        f.write("- ai_models: Store your AI model files (.gguf format)\n")
        f.write("- conversations: Your saved conversations are stored here\n")
        f.write("- logs: Application logs for troubleshooting\n\n")
        f.write("Support:\n")
        f.write("If you encounter any issues, please check the log files in the 'logs' folder.\n")
    
    print(f"README file created at: {readme_path}")

def main():
    parser = argparse.ArgumentParser(description="Build the Local AI Chat application")
    parser.add_argument("--clean", action="store_true", help="Clean build directories before building")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    
    args = parser.parse_args()
    
    # Display start message
    print("=" * 60)
    print("Building Local AI Chat Application")
    print("=" * 60)
    
    if args.clean:
        clean_build_directories()
    
    if not args.skip_deps:
        ensure_dependencies()
    
    create_build_directories()
    build_executable()
    create_user_data_directories()  # Create user data directories AFTER PyInstaller build
    copy_resources()
    create_launcher()
    create_readme()
    
    # Display completion message
    print("\n" + "=" * 60)
    print("Build completed successfully!")
    root_dir = get_root_dir()
    print(f"Output directory: {os.path.abspath(os.path.join(root_dir, 'dist', 'LocalAIChat'))}")
    print("=" * 60)

if __name__ == "__main__":
    main() 