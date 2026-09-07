# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification for compiling Script-Tools into a single standalone executable.
Supports Windows (.exe), Linux, and macOS standalone binary packaging.
"""

from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = [
    "compress_video",
    "pdf_optimizer",
    "dev_doctor",
    "pymupdf",
    "pikepdf",
    "PIL",
    "rich",
]

for pkg in ["pymupdf", "pikepdf", "rich"]:
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

a = Analysis(
    ["tools.py"],
    pathex=["video-compressor", "pdf-optimizer", "vscode-path-doctor"],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter.test", "unittest"],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="tools",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
