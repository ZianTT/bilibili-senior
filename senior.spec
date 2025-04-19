# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata
import platform

if platform.system() == "Windows":
    name = "bilibili-senior-Windows"
elif platform.system() == "Linux":
    name = "bilibili-senior-Linux"
elif platform.system() == "Darwin":
    print(platform.machine())
    if "arm" in platform.machine():
        name = "bilibili-senior-macOS-Apple_Silicon"
    elif "64" in platform.machine():
        name = "bilibili-senior-macOS-Intel"
    else:
        name = "bilibili-senior-macOS"
else:
    name = "bilibili-senior"

import os
version = os.environ.get("version", "unknown")
name = f"{version}-" + name

a = Analysis(
    ["senior.py"],
    pathex=[],
    binaries=[],
    datas=[],
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
    name=name,
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
