import os
import sys
import logging
from pathlib import Path
from system_detector import get_system_info
from installer import install_requirements

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def setup_directories():
    # Get executable directory
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    models_dir = os.path.join(exe_dir, 'ai_models')
    
    # Create directory if it doesn't exist
    os.makedirs(models_dir, exist_ok=True)
    
    return str(models_dir)

def check_persistent_installation():
    # Check if the persistent packages directory exists and contains required packages
    persistent_install_dir = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), 'persistent_packages')
    required_packages = ['flask', 'python-dotenv', 'psutil', 'llama-cpp-python']

    if os.path.exists(persistent_install_dir):
        # Check if all required packages are installed
        installed_packages = os.listdir(persistent_install_dir)
        return all(pkg in installed_packages for pkg in required_packages)
    
    return False

def main():
    try:
        # Setup directories
        models_path = setup_directories()
        logger.info(f"AI Models directory: {models_path}")

        # Get system information
        system_info = get_system_info()
        logger.info(f"Detected system: {system_info}")

        # Check for persistent installation
        if not check_persistent_installation():
            logger.info("First run detected or packages not installed, installing requirements...")
            try:
                logger.debug("Starting installation process...")
                install_requirements(system_info)
                logger.debug("Installation completed.")
            except Exception as e:
                logger.error(f"Installation failed: {e}", exc_info=True)
                input("Press Enter to exit...")  # Keep the window open
                sys.exit(1)
        else:
            logger.info("Required packages are already installed, skipping installation...")

        # Set environment variable for models path
        os.environ['MODELS_DIR'] = models_path

        # Import and run the main application
        try:
            logger.info("Starting application...")
            from local_ai_chat_app import app
            app.run(debug=False)  # Set debug to False for production
        except Exception as e:
            logger.error(f"Application failed to start: {str(e)}", exc_info=True)
            input("Press Enter to exit...")  # Keep the window open
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt detected. Exiting...")
        input("Press Enter to exit...")  # Keep the window open

if __name__ == '__main__':
    main()