# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None
base_dir = Path.cwd()

added_files = [
    ('memory_clean', 'memory'),
    ('config_clean', 'config'),
    ('core', 'core'),
    ('plugins', 'plugins'),
    ('gui', 'gui'),
    ('data', 'data'),
    ('web', 'web'),
    ('actions', 'actions'),
    ('template_sud_uz_catalog.json', '.'),
    ('face.png', '.'),
]

hidden_imports = [
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'docx',
    'google.genai',
    'sqlite3',
    'sounddevice',
    'numpy',
    'core.gemini',
    'core.advokat_kb',
    'core.court_templates',
    'core.licensing',
    'core.case_manager',
    'plugins.legal_draft',
    'plugins.contract_audit',
    'plugins.ish_yuritish',
    'plugins.legal_ocr',
    'plugins.moot_court',
    'plugins.court_calculator'
]

a = Analysis(
    ['main.py'],
    pathex=[str(base_dir)],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Yagona yaxlit (OneFile) EXE: barcha binar fayllar, zip va ma'lumotlar to'g'ridan-to'g'ri bitta .EXE ichiga joylanadi
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AdvokatAI_Standalone',
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
    icon='face.png'
)
