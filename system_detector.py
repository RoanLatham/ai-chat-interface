import platform
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional

@dataclass
class SystemInfo:
    os_type: str
    architecture: str
    gpu_type: Optional[str] = None
    cuda_version: Optional[str] = None
    
def get_nvidia_info():
    try:
        # Try to run nvidia-smi
        nvidia_output = subprocess.check_output(['nvidia-smi'], stderr=subprocess.PIPE)
        return 'nvidia', _parse_cuda_version(nvidia_output.decode())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None, None

def _parse_cuda_version(nvidia_output: str) -> Optional[str]:
    # Parse CUDA version from nvidia-smi output
    import re
    match = re.search(r'CUDA Version: (\d+\.\d+)', nvidia_output)
    return match.group(1) if match else None

def get_apple_silicon():
    if platform.system() == 'Darwin' and platform.processor() == 'arm':
        return 'apple_silicon'
    return None

def get_system_info() -> SystemInfo:
    os_type = platform.system().lower()
    architecture = platform.machine().lower()
    
    # Check for GPU
    gpu_type = None
    cuda_version = None
    
    if os_type == 'darwin' and 'arm' in architecture:
        gpu_type = 'apple_silicon'
    else:
        gpu_type, cuda_version = get_nvidia_info()
    
    return SystemInfo(
        os_type=os_type,
        architecture=architecture,
        gpu_type=gpu_type,
        cuda_version=cuda_version
    )