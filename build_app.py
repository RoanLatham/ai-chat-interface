import subprocess
import sys
import os

def build_executable():
    print("Building LocalAIChat executable...")
    try:
        # Run PyInstaller with our spec file
        subprocess.run(['pyinstaller', 'LocalAIChat.spec'], check=True)
        print("\nBuild successful! Executable can be found in the 'dist' directory")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    build_executable()