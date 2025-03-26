# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import site
import importlib.util
import glob
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# Use the SPEC file directory to determine root directory
# Since __file__ is not available when PyInstaller processes the spec file
spec_dir = os.path.abspath(SPECPATH)
# Go up one level to get to the project root (from build_tools to project root)
root_dir = os.path.dirname(spec_dir)
print(f"LocalAIChat Spec: Root directory determined as: {root_dir}")

# Ensure we're using absolute paths for everything
build_dir = os.path.join(root_dir, "build")
dist_dir = os.path.join(root_dir, "dist")

block_cipher = None

# Try to find the llama_cpp package
llama_cpp_datas = []
llama_cpp_binaries = []

try:
    llama_cpp_spec = importlib.util.find_spec('llama_cpp')
    if llama_cpp_spec and llama_cpp_spec.origin:
        llama_cpp_path = os.path.dirname(llama_cpp_spec.origin)
        print(f"LocalAIChat Spec: Found llama_cpp at: {llama_cpp_path}")
        
        # Add lib directory
        llama_cpp_lib_path = os.path.join(llama_cpp_path, 'lib')
        if os.path.exists(llama_cpp_lib_path):
            print(f"LocalAIChat Spec: Found llama_cpp/lib at: {llama_cpp_lib_path}")
            for root, dirs, files in os.walk(llama_cpp_lib_path):
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_dir = os.path.join('llama_cpp', 'lib', os.path.relpath(root, llama_cpp_lib_path))
                    llama_cpp_datas.append((src_file, dst_dir))
        
        # Add DLLs
        for dll_file in glob.glob(os.path.join(llama_cpp_path, "*.dll")):
            if os.path.exists(dll_file):
                print(f"LocalAIChat Spec: Found DLL: {dll_file}")
                llama_cpp_binaries.append((dll_file, '.'))
except Exception as e:
    print(f"LocalAIChat Spec: Error finding llama_cpp: {e}")

# Collect standard datas and binaries with absolute paths
additional_datas = [
    (os.path.join(root_dir, 'system-prompt.txt'), '.'),
    (os.path.join(root_dir, 'chat-interface.html'), '.'),
    (os.path.join(root_dir, 'conversation.py'), '.'),
]

if os.path.exists(os.path.join(root_dir, 'icon')):
    additional_datas.append((os.path.join(root_dir, 'icon'), 'icon'))

a = Analysis(
    [os.path.join(root_dir, 'local-ai-chat-app.py')],
    pathex=[root_dir],  # Add the root directory to the Python path
    binaries=llama_cpp_binaries,
    datas=additional_datas + llama_cpp_datas,
    hiddenimports=['llama_cpp', 'llama_cpp.llama_cpp'],
    hookspath=[os.path.join(root_dir, 'build_tools')],  # Use absolute path for hooks
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LocalAIChat',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(root_dir, 'icon/AII-console-icon.ico') if os.path.exists(os.path.join(root_dir, 'icon/AII-console-icon.ico')) else (os.path.join(root_dir, 'icon/AII-icon.ico') if os.path.exists(os.path.join(root_dir, 'icon/AII-icon.ico')) else None),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LocalAIChat',
    noconfirm=True,
) 