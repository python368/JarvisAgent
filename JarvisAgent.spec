# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for JarvisAgent macOS application.
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

APP_NAME = "JarvisAgent"
APP_VERSION = "2.0.0"
BUNDLE_IDENTIFIER = "com.jarvisagent.app"

# Get the base path
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(SPEC))

datas = []
hiddenimports = [
    'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'PyQt6.sip',
    'models.base_client', 'models.openai_client', 'models.anthropic_client',
    'models.ollama_client', 'models.google_client', 'models.model_router',
    'tools.screenshot', 'tools.mouse', 'tools.keyboard', 'tools.app_control',
    'tools.file_manager', 'agent.agent', 'agent.planner', 'agent.task_manager',
    'agent.dialog_manager', 'agent.memory', 'config.app_config', 'utils.logger',
    'openai', 'anthropic', 'google.generativeai', 'google.genai', 'mss', 'PIL', 'pyautogui', 'requests',
    'numpy', 'certifi', 'charset_normalizer', 'idna', 'urllib3',
]

a = Analysis(
    ['main.py'],
    pathex=[os.path.dirname(os.path.abspath(SPEC))],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'IPython', 'notebook'],
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
    name='JarvisAgent',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    argv_emulation=True,
)

app = BUNDLE(
    exe,
    name=f'{APP_NAME}.app',
    bundle_identifier=BUNDLE_IDENTIFIER,
    info_plist={
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': 'Jarvis Agent',
        'CFBundleIdentifier': BUNDLE_IDENTIFIER,
        'CFBundleVersion': APP_VERSION,
        'CFBundleShortVersionString': APP_VERSION,
        'CFBundlePackageType': 'APPL',
        'CFBundleExecutable': 'JarvisAgent',
        'LSMinimumSystemVersion': '10.15',
        'NSHighResolutionCapable': True,
        'NSPrincipalClass': 'NSApplication',
        'NSHumanReadableCopyright': 'Copyright 2024 Jarvis Agent.',
        'LSApplicationCategoryType': 'public.app-category.productivity',
        'NSSupportsAutomaticTermination': True,
        'NSSupportsSuddenTermination': False,
    },
)
