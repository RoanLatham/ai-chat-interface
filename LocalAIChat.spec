# -*- mode: python ; coding: utf-8 -*-
import os
import shutil
from pathlib import Path

block_cipher = None

# Create a temporary directory for build assets
temp_dir = Path('build_assets')
temp_dir.mkdir(exist_ok=True)

# Create empty directories structure
(temp_dir / 'conversations').mkdir(exist_ok=True)

# Copy only the example conversation
example_conv = 'c04c9317-903d-4014-a128-c7dd4bca216f.pickle'
if os.path.exists(f'conversations/{example_conv}'):
    shutil.copy2(f'conversations/{example_conv}', temp_dir / 'conversations' / example_conv)

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('system_detector.py', '.'),
        ('installer.py', '.'),
        ('local_ai_chat_app.py', '.'),
        ('system-prompt.txt', '.'),
        ('chat-interface.html', '.'),
        ('icon/AII-icon.ico', 'icon'),
        ('icon/AII-console-icon.ico', 'icon'),
        (str(temp_dir / 'conversations'), 'conversations'),
    ],
    hiddenimports=[
        'torch',
        'psutil',
        'flask',
        'logging',
        'datetime',
        'json',
        'dataclasses',

    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LocalAIChat',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon/AII-icon.ico'
)

# Clean up temporary directory after build
def cleanup():
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

import atexit
atexit.register(cleanup)