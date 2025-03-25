from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs
import os
import importlib.util
import site

# Collect all data files from the package
datas = collect_data_files('llama_cpp')

# Collect all dynamic libraries
binaries = collect_dynamic_libs('llama_cpp')

# Specifically ensure that the 'lib' directory is collected
llama_cpp_found = False
try:
    llama_cpp_spec = importlib.util.find_spec('llama_cpp')
    if llama_cpp_spec and llama_cpp_spec.origin:
        llama_cpp_path = os.path.dirname(llama_cpp_spec.origin)
        llama_cpp_lib_path = os.path.join(llama_cpp_path, 'lib')
        
        if os.path.exists(llama_cpp_lib_path):
            # Add all files in the lib directory
            for root, dirs, files in os.walk(llama_cpp_lib_path):
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_dir = os.path.join('llama_cpp', 'lib', os.path.relpath(root, llama_cpp_lib_path))
                    datas.append((src_file, dst_dir))
            llama_cpp_found = True
except (ImportError, AttributeError):
    pass

if not llama_cpp_found:
    # Try site-packages as a fallback
    for site_dir in site.getsitepackages():
        llama_cpp_path = os.path.join(site_dir, 'llama_cpp')
        llama_cpp_lib_path = os.path.join(llama_cpp_path, 'lib')
        
        if os.path.exists(llama_cpp_lib_path):
            # Add all files in the lib directory
            for root, dirs, files in os.walk(llama_cpp_lib_path):
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_dir = os.path.join('llama_cpp', 'lib', os.path.relpath(root, llama_cpp_lib_path))
                    datas.append((src_file, dst_dir))
            break 