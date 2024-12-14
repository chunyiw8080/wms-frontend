# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['windows\\main.py'],
    pathex=['backendRequests', 'employee', 'history', 'inventory', 'operation_logs', 'orders', 'project', 'provider', 'users', 'utils', 'windows', 'config'],
    binaries=[],
    datas=[('resources/icons/*.svg', 'resources/icons'), ('resources/images/*.jpg', 'resources/images'), ('resources/logo/*.png', 'resources/logo')],
    hiddenimports=[],
    hookspath=[],
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
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources\\logo\\logo.png'],
)
