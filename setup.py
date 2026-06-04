# setup.py - JarvisAgent Package Installer
"""
JarvisAgent - AI Computer Control Agent for macOS

Install:
    pip install -e .           # Development mode
    pip install .             # Production mode
    pip install . --verbose    # Verbose output

Build .app:
    python setup.py build_app  # Creates dist/JarvisAgent.app
"""

from setuptools import setup, find_packages
import os

# Read long description from README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="JarvisAgent",
    version="2.0.0",
    description="AI Computer Control Agent for macOS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Jarvis Agent Team",
    author_email="contact@jarvisagent.app",
    url="https://github.com/python368/JarvisAgent",
    packages=find_packages(exclude=["tests", "tests/*"]),
    python_requires=">=3.10",
    install_requires=[
        "PyQt6>=6.6.0",
        "requests>=2.31.0",
        "openai>=1.12.0",
        "anthropic>=0.18.0",
        "google-generativeai>=0.3.0",
        "pyautogui>=0.9.54",
        "Pillow>=10.0.0",
        "numpy>=1.24.0",
        "mss>=9.0.1",
    ],
    extras_require={
        "macos": ["pyobjc-framework-Quartz>=9.0"],
        "dev": ["pytest>=7.0", "pyinstaller>=6.0.0"],
    },
    entry_points={
        "console_scripts": [
            "jarvis=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)