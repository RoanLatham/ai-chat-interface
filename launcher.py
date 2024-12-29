import os
import sys
import logging
import subprocess
import shutil
from pathlib import Path
from system_detector import get_system_info
from installer import install_requirements

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def setup_directories():
    base_dir = Path(os.path.dirname(os.path.abspath(sys.executable)))
    venv_dir = base_dir / 'venv'
    app_dir = base_dir / 'app'
    icon_dir = app_dir / 'icon'  # Add icon directory under app
    
    # Create necessary directories if they don't exist
    app_dir.mkdir(exist_ok=True)
    icon_dir.mkdir(exist_ok=True)
    
    # Copy required files to app directory if they don't exist
    required_files = [
        'local_ai_chat_app.py',
        'conversation.py',
        'system-prompt.txt',
        'chat-interface.html'
    ]
    
    # Copy main files only if they don't already exist
    for file in required_files:
        src = get_resource_path(file)
        dst = app_dir / file
        if not dst.exists():
            logger.info(f"Copying {file} to {dst}")
            shutil.copy2(src, dst)
        else:
            logger.info(f"{file} already exists at {dst}, skipping copy.")
    
    # Copy icon files only if they don't already exist
    icon_files = [
        'AII-icon.ico',
        'AII-console-icon.ico'
    ]
    
    for icon in icon_files:
        src = get_resource_path(os.path.join('icon', icon))
        dst = icon_dir / icon
        if not dst.exists():
            logger.info(f"Copying icon {icon} to {dst}")
            shutil.copy2(src, dst)
        else:
            logger.info(f"Icon {icon} already exists at {dst}, skipping copy.")
    
    return str(venv_dir), str(app_dir)

def check_venv_installation(venv_dir):
    """Check if venv exists and has required packages"""
    venv_dir = Path(venv_dir)
    python_exe = venv_dir / ('Scripts' if os.name == 'nt' else 'bin') / ('python.exe' if os.name == 'nt' else 'python')
    
    if not python_exe.exists():
        return False
        
    try:
        cmd = [str(python_exe), '-c', 
               'import flask; import dotenv; import psutil; import llama_cpp']
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    try:
        # Setup directories
        venv_path, app_path = setup_directories()
        logger.info(f"Virtual environment path: {venv_path}")
        logger.info(f"Application directory: {app_path}")

        # Get system information
        system_info = get_system_info()
        logger.info(f"Detected system: {system_info}")

        # Check for venv installation
        if not check_venv_installation(venv_path):
            logger.info("Virtual environment not found or incomplete, installing requirements...")
            try:
                install_requirements(system_info)
            except Exception as e:
                logger.error(f"Installation failed: {str(e)}")
                print("\nPress Enter to exit...")
                input()
                sys.exit(1)
        
        # Launch the application using the venv Python
        python_exe = str(Path(venv_path) / ('Scripts' if os.name == 'nt' else 'bin') / ('python.exe' if os.name == 'nt' else 'python'))
        app_script = str(Path(app_path) / 'local_ai_chat_app.py')
        
        try:
            subprocess.run([python_exe, app_script, '--packaged'], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Application failed to start: {str(e)}")
            print("\nApplication failed to start. Check the error messages above.")
            print("Press Enter to exit...")
            input()
            sys.exit(1)

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print("\nAn unexpected error occurred. Check the error messages above.")
        print("Press Enter to exit...")
        input()
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
        print("Press Enter to exit...")
        input()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        print("\nA fatal error occurred. Check the error messages above.")
        print("Press Enter to exit...")
        input()
        sys.exit(1)