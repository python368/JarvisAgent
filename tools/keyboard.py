"""Keyboard control tool for typing and key operations.

This module provides keyboard control functionality for the Jarvis agent,
including typing, key presses, hotkeys, and key combinations.
"""

from __future__ import annotations

import sys
from typing import Optional, List

# Try to import pyautogui, but handle environments without display
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
except Exception:
    PYAUTOGUI_AVAILABLE = False


class KeyboardTool:
    """Tool for controlling keyboard input."""
    
    def __init__(self):
        if not PYAUTOGUI_AVAILABLE:
            raise ImportError("pyautogui is required for keyboard control. Install: pip install pyautogui")
    
    def typewrite(self, text: str, interval: float = 0) -> None:
        """Type text character by character."""
        pyautogui.write(text, interval=interval)
    
    def press(self, *keys: str) -> None:
        """Press a key or key combination."""
        for key in keys:
            pyautogui.press(key)
    
    def key_down(self, key: str) -> None:
        """Press and hold a key."""
        pyautogui.keyDown(key)
    
    def key_up(self, key: str) -> None:
        """Release a held key."""
        pyautogui.keyUp(key)
    
    def hotkey(self, *keys: str, interval: float = 0) -> None:
        """Press a key combination (all keys down then up together)."""
        pyautogui.hotkey(*keys, interval=interval)
    
    def copy(self) -> None:
        """Copy (Ctrl+C / Cmd+C)."""
        if sys.platform == "darwin":
            self.hotkey("command", "c")
        else:
            self.hotkey("ctrl", "c")
    
    def paste(self) -> None:
        """Paste (Ctrl+V / Cmd+V)."""
        if sys.platform == "darwin":
            self.hotkey("command", "v")
        else:
            self.hotkey("ctrl", "v")
    
    def select_all(self) -> None:
        """Select all (Ctrl+A / Cmd+A)."""
        if sys.platform == "darwin":
            self.hotkey("command", "a")
        else:
            self.hotkey("ctrl", "a")
    
    def enter(self) -> None:
        """Press Enter/Return key."""
        self.press("enter")
    
    def escape(self) -> None:
        """Press Escape key."""
        self.press("esc")
    
    def tab(self) -> None:
        """Press Tab key."""
        self.press("tab")
    
    def space(self) -> None:
        """Press Space key."""
        self.press("space")
    
    def backspace(self) -> None:
        """Press Backspace key."""
        self.press("backspace")
    
    def arrow_up(self) -> None:
        """Press Up arrow key."""
        self.press("up")
    
    def arrow_down(self) -> None:
        """Press Down arrow key."""
        self.press("down")
    
    def arrow_left(self) -> None:
        """Press Left arrow key."""
        self.press("left")
    
    def arrow_right(self) -> None:
        """Press Right arrow key."""
        self.press("right")


# Singleton instance
_keyboard_tool: Optional[KeyboardTool] = None


def get_keyboard_tool() -> KeyboardTool:
    """Get or create the singleton keyboard tool instance."""
    global _keyboard_tool
    if _keyboard_tool is None:
        _keyboard_tool = KeyboardTool()
    return _keyboard_tool


def typewrite(text: str, interval: float = 0) -> None:
    """Convenience function to type text."""
    get_keyboard_tool().typewrite(text, interval=interval)


def press(*keys: str) -> None:
    """Convenience function to press keys."""
    get_keyboard_tool().press(*keys)


def hotkey(*keys: str) -> None:
    """Convenience function to press key combination."""
    get_keyboard_tool().hotkey(*keys)