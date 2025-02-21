# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['automacao_exe.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\mathe\\AppData\\Local\\ms-playwright', 'ms-playwright'), ('C:\\Users\\mathe\\Miniconda3\\envs\\automacao\\Lib\\site-packages\\browser_use\\dom', 'browser_use\\dom')],
    hiddenimports=['pydantic.deprecated.decorator'],
    hookspath=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Automação Web.exe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.ico'],
)
