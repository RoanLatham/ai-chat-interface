# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\ComputerScience\\LocalAIChat\\local-ai-chat-app.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\ComputerScience\\LocalAIChat\\system-prompt.txt', '.'), ('D:\\ComputerScience\\LocalAIChat\\chat-interface.html', '.'), ('D:\\ComputerScience\\LocalAIChat\\conversation.py', '.'), ('D:\\ComputerScience\\LocalAIChat\\icon', 'icon')],
    hiddenimports=[],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

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
    icon=['D:\\ComputerScience\\LocalAIChat\\icon\\AII-console-icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LocalAIChat',
)
