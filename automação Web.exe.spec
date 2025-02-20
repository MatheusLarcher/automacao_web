# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['automacao_exe.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\Matheus\\AppData\\Local\\ms-playwright', 'ms-playwright'), ('C:\\Users\\Matheus\\Miniconda3\\envs\\automacao\\Lib\\site-packages\\browser_use\\dom', 'browser_use\\dom')],
    hiddenimports=['pydantic.deprecated.decorator'],
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
    name='automação Web.exe',
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
