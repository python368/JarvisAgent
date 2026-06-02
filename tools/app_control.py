"""Application control tool for controlling applications and windows.

This module provides functionality for the Jarvis agent to interact with
applications, windows, and perform application-level operations on macOS.
"""

from __future__ import annotations

import subprocess
import sys
import os
from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import Enum


class Platform(Enum):
    """Supported platforms."""
    MACOS = "darwin"


@dataclass
class Window:
    """Represents a window."""
    title: str
    process_name: str
    pid: int
    x: int
    y: int
    width: int
    height: int


class AppControlTool:
    """Tool for controlling applications and windows on macOS."""
    
    def __init__(self):
        """Initialize the app control tool."""
        self._platform = "macos" if sys.platform == "darwin" else "other"
    
    def launch_app(self, app_path: str, args: Optional[List[str]] = None) -> bool:
        """Launch an application.
        
        Args:
            app_path: Path to the application or app name.
            args: Optional command-line arguments.
            
        Returns:
            True if launch was successful.
        """
        try:
            cmd = ["open", "-a", app_path] if os.path.exists(app_path) else ["open", "-a", app_path]
            if args:
                cmd.extend(args)
            subprocess.Popen(cmd)
            return True
        except Exception:
            return False
    
    def open_url(self, url: str) -> bool:
        """Open a URL in the default browser."""
        try:
            subprocess.Popen(["open", url])
            return True
        except Exception:
            return False
    
    def switch_app(self, app_name: str) -> bool:
        """Switch to an application by name."""
        try:
            script = f'tell application "{app_name}" to activate'
            subprocess.run(["osascript", "-e", script], check=True)
            return True
        except Exception:
            return False
    
    def close_window(self) -> bool:
        """Close the current window."""
        try:
            from tools.keyboard import get_keyboard_tool
            keyboard = get_keyboard_tool()
            if self._platform == "macos":
                keyboard.hotkey("command", "w")
                return True
        except Exception:
            pass
        return False
    
    def minimize_window(self) -> bool:
        """Minimize the current window."""
        try:
            script = 'tell application "System Events" to set miniaturized of (first window of (first process whose frontmost is true)) to true'
            subprocess.run(["osascript", "-e", script], check=True)
            return True
        except Exception:
            return False


# Singleton instance
_app_tool: Optional[AppControlTool] = None


def get_app_tool() -> AppControlTool:
    """Get or create the singleton app control tool instance."""
    global _app_tool
    if _app_tool is None:
        _app_tool = AppControlTool()
    return _app_tool