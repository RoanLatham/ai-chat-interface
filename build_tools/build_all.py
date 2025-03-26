"""
Main build script for Local AI Chat App
This script orchestrates the entire build process:
1. Builds the Python application using PyInstaller
2. Creates an installer using Inno Setup (Windows)
"""

import os
import sys
import platform
import subprocess
import argparse
import shutil
import time

# Get the root directory (parent of build_tools)
def get_root_dir():
    """Get the root directory of the project"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def check_requirements():
    """Check if all required tools are installed"""
    print("Checking requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("Error: Python 3.8 or higher is required.")
        return False
    
    # Check for PyInstaller
    try:
        subprocess.check_call([sys.executable, "-c", "import PyInstaller"], 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL)
    except:
        print("PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        except:
            print("Error: Failed to install PyInstaller.")
            return False
    
    # Check for Inno Setup on Windows
    if platform.system() == "Windows":
        inno_path = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
        alt_inno_path = r"C:\Program Files\Inno Setup 6\ISCC.exe"
        
        if not (os.path.exists(inno_path) or os.path.exists(alt_inno_path)):
            print("Warning: Inno Setup not found at the expected location.")
            print("If you want to create an installer, please download and install Inno Setup from:")
            print("https://jrsoftware.org/isdl.php")
            
            user_choice = input("Continue without installer creation? (y/n): ")
            if user_choice.lower() != 'y':
                return False
    
    print("Requirements check passed!")
    return True

def build_application():
    """Build the Python application using build.py"""
    print("\n" + "=" * 60)
    print("Building Python Application...")
    print("=" * 60)
    
    root_dir = get_root_dir()
    build_script = os.path.join(root_dir, "build_tools", "build.py")
    
    # Save current directory
    original_dir = os.getcwd()
    
    try:
        # Change to root directory before running build script
        os.chdir(root_dir)
        print(f"Build_all: Changed working directory to: {root_dir}")
        
        # Use absolute path to build script
        subprocess.check_call([sys.executable, build_script, "--clean"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build_all: Error: Failed to build application: {e}")
        return False
    finally:
        # Restore original directory
        os.chdir(original_dir)

def create_installer():
    """Create an installer using Inno Setup (Windows only)"""
    if platform.system() != "Windows":
        print("Installer creation is currently only supported on Windows.")
        return False
    
    print("\n" + "=" * 60)
    print("Creating Windows Installer...")
    print("=" * 60)
    
    root_dir = get_root_dir()
    
    # Find Inno Setup compiler
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe"
    ]
    
    inno_path = None
    for path in inno_paths:
        if os.path.exists(path):
            inno_path = path
            break
    
    if not inno_path:
        print("Error: Inno Setup not found. Skipping installer creation.")
        return False
    
    # Save current directory
    original_dir = os.getcwd()
    
    try:
        # Change to root directory before running installer script
        os.chdir(root_dir)
        print(f"Build_all: Changed working directory to: {root_dir}")
        
        # Set environment variable for the installer script
        os.environ["BuildRootDir"] = root_dir
        
        # Use absolute path to installer script
        installer_script = os.path.join(root_dir, "build_tools", "installer_script.iss")
        cmd = [inno_path, f"/O{os.path.join(root_dir, 'Output')}", installer_script]
        print(f"Build_all: Running command: {' '.join(cmd)}")
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build_all: Error: Failed to create installer: {e}")
        return False
    finally:
        # Restore original directory
        os.chdir(original_dir)

def create_distribution_package():
    """Create a zip file of the application for non-Windows platforms"""
    if platform.system() == "Windows":
        # We're already creating an installer on Windows
        return True
    
    print("\n" + "=" * 60)
    print("Creating Distribution Package...")
    print("=" * 60)
    
    import zipfile
    root_dir = get_root_dir()
    
    # Save current directory
    original_dir = os.getcwd()
    
    try:
        # Change to root directory
        os.chdir(root_dir)
        print(f"Build_all: Changed working directory to: {root_dir}")
        
        app_dir = os.path.join(root_dir, "dist", "LocalAIChat")
        zip_filename = os.path.join(root_dir, "dist", "LocalAIChat.zip")
        
        # Check if paths exist
        if not os.path.exists(app_dir):
            print(f"Build_all: Error: Application directory not found at: {app_dir}")
            return False
            
        print(f"Build_all: Creating zip file: {zip_filename}")
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
            
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(app_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, os.path.dirname(app_dir))
                    print(f"Build_all: Adding: {rel_path}")
                    zipf.write(file_path, rel_path)
        
        print(f"Build_all: Distribution package created: {zip_filename}")
        return True
    except Exception as e:
        print(f"Build_all: Error: Failed to create distribution package: {e}")
        return False
    finally:
        # Restore original directory
        os.chdir(original_dir)

def main():
    parser = argparse.ArgumentParser(description="Build the Local AI Chat application and installer")
    parser.add_argument("--no-installer", action="store_true", help="Skip installer creation")
    parser.add_argument("--no-app-build", action="store_true", help="Skip application build (use existing build)")
    
    args = parser.parse_args()
    
    # Display start message
    print("=" * 60)
    print("Local AI Chat - Complete Build Process")
    print("=" * 60)
    print(f"Build_all: Platform: {platform.system()} {platform.release()}")
    print(f"Build_all: Python: {sys.version.split()[0]}")
    
    # Ensure we have all requirements
    if not check_requirements():
        sys.exit(1)
    
    start_time = time.time()
    root_dir = get_root_dir()
    
    # Step 1: Build the application
    app_built = True
    if not args.no_app_build:
        app_built = build_application()
        if not app_built:
            print("Application build failed. Stopping the build process.")
            sys.exit(1)
    else:
        print("Skipping application build.")
    
    # Step 2: Create the installer
    if not args.no_installer and app_built:
        if platform.system() == "Windows":
            installer_created = create_installer()
            if not installer_created:
                print("Note: Installer creation failed but the application build is available.")
        else:
            # Create a zip package for non-Windows platforms
            package_created = create_distribution_package()
            if not package_created:
                print("Note: Package creation failed but the application build is available.")
    
    # Display completion message
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"Build_all: Build process completed in {elapsed_time:.2f} seconds!")
    
    if app_built:
        app_path = os.path.abspath(os.path.join(root_dir, "dist", "LocalAIChat"))
        print(f"Build_all: Application build available at: {app_path}")
        
        if not args.no_installer and platform.system() == "Windows":
            installer_path = os.path.abspath(os.path.join(root_dir, "Output", "LocalAIChat_Setup.exe"))
            if os.path.exists(installer_path):
                print(f"Build_all: Installer available at: {installer_path}")
        elif not args.no_installer:
            zip_path = os.path.abspath(os.path.join(root_dir, "dist", "LocalAIChat.zip"))
            if os.path.exists(zip_path):
                print(f"Build_all: Distribution package available at: {zip_path}")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 