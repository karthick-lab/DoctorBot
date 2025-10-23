# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:/Users/admin/Desktop/PythonProjects/Doctor Bot/main.py'],
    pathex=[],
    binaries=[('C:/Users/admin/gpt4all/lib/libllmodel.dll', 'gpt4all/llmodel_DO_NOT_MODIFY/build')],
    datas=[],
    hiddenimports=['gpt4all._pyllmodel'],
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
    name='DoctorBot',
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
)
