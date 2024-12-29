# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('system_detector.py', '.'),
        ('installer.py', '.'),
        ('local_ai_chat_app.py', '.'),
        ('conversation.py', '.'),
        ('system-prompt.txt', '.'),
        ('chat-interface.html', '.'),
        ('icon/AII-icon.ico', 'icon'),
        ('icon/AII-console-icon.ico', 'icon'),
    ],
    hiddenimports=[
        'venv',
        'subprocess',
        'logging',
        'pathlib',
        'platform',
        'dataclasses'
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