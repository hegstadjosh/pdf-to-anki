# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\socce\\Documents\\#Spring 25\\pdf2anki\\app.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\socce\\Documents\\#Spring 25\\pdf2anki\\.env.example', '.env.example')],
    hiddenimports=['en_core_web_sm'],
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
    a.binaries,
    a.datas,
    [],
    name='PDFToAnki',
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
)
