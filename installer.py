import sys
import logging
import os
import urllib.request
import subprocess
import tempfile
import shutil
from pathlib import Path
from importlib import import_module, util

logger = logging.getLogger(__name__)

def download_wheel(package_name, target_dir):
    """Download a wheel file for the given package"""
    url = f"https://pypi.org/pypi/{package_name}/json"
    
    try:
        with urllib.request.urlopen(url) as response:
            import json
            data = json.loads(response.read())
            
            # Get the latest version's wheel URL
            for url in data['urls']:
                if url['packagetype'] == 'bdist_wheel':
                    wheel_url = url['url']
                    wheel_name = url['filename']
                    wheel_path = os.path.join(target_dir, wheel_name)
                    
                    logger.info(f"Downloading {wheel_name}...")
                    print(f"Downloading {wheel_name}...")  # Direct console output
                    urllib.request.urlretrieve(wheel_url, wheel_path)
                    return wheel_path
    except Exception as e:
        logger.error(f"Error downloading wheel for {package_name}: {str(e)}")
        print(f"Error downloading wheel for {package_name}: {str(e)}")  # Direct console output
        raise

def install_wheel(wheel_path, target_dir):
    """Install a wheel file using pip in a subprocess with real-time output"""
    logger.info(f"Installing {os.path.basename(wheel_path)}...")
    print(f"\nInstalling {os.path.basename(wheel_path)}...")  # Direct console output
    
    python_exe = sys.executable
    cmd = [python_exe, '-m', 'pip', 'install', 
           '--target', target_dir, 
           '--no-deps',
           '--no-cache-dir',  # Added to prevent caching issues
           wheel_path]
    
    try:
        # Use Popen for real-time output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )

        # Print output in real-time
        while True:
            output = process.stdout.readline()
            error = process.stderr.readline()
            
            if output:
                print(output.strip())
                logger.info(output.strip())
            if error:
                print(error.strip(), file=sys.stderr)
                logger.error(error.strip())
            
            # Check if process has finished
            if process.poll() is not None:
                break
        
        # Get the return code
        return_code = process.returncode
        if return_code != 0:
            # Get any remaining error output
            _, stderr = process.communicate()
            error_msg = f"Installation failed with return code {return_code}"
            if stderr:
                error_msg += f": {stderr}"
            raise subprocess.CalledProcessError(return_code, cmd, stderr=stderr)
            
    except Exception as e:
        logger.error(f"Error installing wheel: {str(e)}")
        print(f"Error installing wheel: {str(e)}")  # Direct console output
        raise

def install_requirements(system_info):
    logger.info("Starting requirements installation...")
    print("\nStarting requirements installation...")  # Direct console output
    
    # Define a directory for persistent installations
    base_dir = os.path.dirname(os.path.abspath(sys.executable))
    persistent_install_dir = os.path.join(base_dir, 'persistent_packages')
    os.makedirs(persistent_install_dir, exist_ok=True)
    
    logger.info(f"Installing to: {persistent_install_dir}")
    print(f"Installing to: {persistent_install_dir}")  # Direct console output
    
    # Base requirements
    base_requirements = [
        'flask',
        'python-dotenv',
        'psutil'
    ]
    
    try:
        # Create a temporary directory for downloading wheels
        with tempfile.TemporaryDirectory() as temp_dir:
            # Install base requirements
            logger.info("Installing base requirements...")
            print("\nInstalling base requirements...")  # Direct console output
            for req in base_requirements:
                wheel_path = download_wheel(req, temp_dir)
                install_wheel(wheel_path, persistent_install_dir)
            
            # Install llama-cpp-python based on system
            if system_info.gpu_type == 'nvidia':
                logger.info("Installing CUDA version of llama-cpp-python...")
                print("\nInstalling CUDA version of llama-cpp-python...")  # Direct console output
                os.environ['CMAKE_ARGS'] = '-DLLAMA_CUBLAS=on'
                wheel_path = download_wheel('llama-cpp-python', temp_dir)
                install_wheel(wheel_path, persistent_install_dir)
                
            elif system_info.gpu_type == 'apple_silicon':
                logger.info("Installing Metal version of llama-cpp-python...")
                print("\nInstalling Metal version of llama-cpp-python...")  # Direct console output
                os.environ['CMAKE_ARGS'] = '-DLLAMA_METAL=on'
                wheel_path = download_wheel('llama-cpp-python', temp_dir)
                install_wheel(wheel_path, persistent_install_dir)
                
            else:
                logger.info("Installing CPU-only version of llama-cpp-python...")
                print("\nInstalling CPU-only version of llama-cpp-python...")  # Direct console output
                wheel_path = download_wheel('llama-cpp-python', temp_dir)
                install_wheel(wheel_path, persistent_install_dir)
        
        logger.info("All requirements installed successfully")
        print("\nAll requirements installed successfully")  # Direct console output
        
        # Verify installation
        sys.path.append(persistent_install_dir)
        try:
            import flask
            import dotenv
            import psutil
            import llama_cpp
            logger.info("Installation verification successful")
            print("Installation verification successful")
            return True
        except ImportError as e:
            logger.error(f"Installation verification failed: {str(e)}")
            print(f"Installation verification failed: {str(e)}")
            return False
        
    except Exception as e:
        logger.error(f"Unexpected error during installation: {str(e)}", exc_info=True)
        print(f"Unexpected error during installation: {str(e)}")  # Direct console output
        raise
