import os
import sys
import venv
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class VenvInstaller:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.venv_dir = self.base_dir / 'venv'
        
        # Get system Python path instead of using sys.executable
        self.system_python = self._get_system_python()
        if not self.system_python:
            raise RuntimeError("Could not find Python installation on system")
            
        self.python_exe = str(self.venv_dir / 'Scripts' / 'python.exe') if os.name == 'nt' else str(self.venv_dir / 'bin' / 'python')
        self.pip_exe = str(self.venv_dir / 'Scripts' / 'pip.exe') if os.name == 'nt' else str(self.venv_dir / 'bin' / 'pip')

    def _get_system_python(self):
        """Find system Python installation"""
        if os.name == 'nt':  # Windows
            try:
                # Try to get Python path from py launcher
                result = subprocess.run(['py', '-3', '-c', 'import sys; print(sys.executable)'],
                                     capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
            except FileNotFoundError:
                pass
            
            # Check common Windows locations
            possible_paths = [
                os.path.expandvars(r'%LocalAppData%\Programs\Python\Python3*\python.exe'),
                r'C:\Python3*\python.exe',
                os.path.expandvars(r'%ProgramFiles%\Python3*\python.exe'),
                os.path.expandvars(r'%ProgramFiles(x86)%\Python3*\python.exe')
            ]
            
            import glob
            for pattern in possible_paths:
                matches = sorted(glob.glob(pattern), reverse=True)  # Latest version first
                if matches:
                    return matches[0]
                    
        else:  # Unix-like systems
            try:
                # Try common Unix paths
                for path in ['/usr/bin/python3', '/usr/local/bin/python3']:
                    if os.path.exists(path):
                        return path
            except Exception:
                pass
                
        return None

    def create_venv(self):
        """Create a virtual environment using system Python"""
        logger.info("Creating virtual environment...")
        print(f"Creating virtual environment using Python at: {self.system_python}")
        
        try:
            # First, ensure pip is up to date in system Python
            # subprocess.run([self.system_python, '-m', 'pip', 'install', '--upgrade', 'pip'],
            #              check=True)
            
            # Create venv using system Python
            subprocess.run([self.system_python, '-m', 'venv', str(self.venv_dir)],
                         check=True)
            
            # Upgrade pip in the new venv
            # self.run_pip_command(['install', '--upgrade', 'pip'])
            subprocess.run([self.python_exe , '-m', 'pip', 'install', '--upgrade', 'pip'],
                         check=True)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create virtual environment: {e}")
            raise

    def run_pip_command(self, args):
        """Run a pip command in the virtual environment"""
        cmd = [self.pip_exe] + args
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )

        while True:
            output = process.stdout.readline()
            error = process.stderr.readline()
            
            if output:
                print(output.strip())
                logger.info(output.strip())
            if error:
                print(error.strip(), file=sys.stderr)
                logger.error(error.strip())
            
            if process.poll() is not None:
                break

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd)

    def install_requirements(self, system_info):
        """Install all required packages"""
        logger.info("Installing requirements...")
        print("\nInstalling requirements...")

        # Install base requirements
        base_requirements = [
            'flask',
            'python-dotenv',
            'psutil'
        ]

        for req in base_requirements:
            self.run_pip_command(['install', req])

        # Install llama-cpp-python with appropriate flags
        if system_info.gpu_type == 'nvidia':
            logger.info("Installing CUDA version of llama-cpp-python...")
            os.environ['CMAKE_ARGS'] = '-DLLAMA_CUBLAS=on'
            self.run_pip_command(['install', 'llama-cpp-python'])
            
        elif system_info.gpu_type == 'apple_silicon':
            logger.info("Installing Metal version of llama-cpp-python...")
            os.environ['CMAKE_ARGS'] = '-DLLAMA_METAL=on'
            self.run_pip_command(['install', 'llama-cpp-python'])
            
        else:
            logger.info("Installing CPU-only version of llama-cpp-python...")
            self.run_pip_command(['install', 'llama-cpp-python'])

    def verify_installation(self):
        """Verify that all required packages are installed"""
        cmd = [self.python_exe, '-c', 
               'import flask; import dotenv; import psutil; import llama_cpp']
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info("Installation verification successful")
            print("Installation verification successful")
            return True
        except subprocess.CalledProcessError:
            logger.error("Installation verification failed")
            print("Installation verification failed")
            return False

def install_requirements(system_info):
    """Main installation function"""
    base_dir = os.path.dirname(os.path.abspath(sys.executable))
    installer = VenvInstaller(base_dir)
    
    try:
        installer.create_venv()
        installer.install_requirements(system_info)
        return installer.verify_installation()
    except Exception as e:
        logger.error(f"Installation failed: {str(e)}")
        print(f"Installation failed: {str(e)}")
        raise
