"""Mouse control tool for controlling cursor movement and clicks.

This module provides mouse control functionality for the Jarvis agent,
including moving, clicking, scrolling, and dragging operations.
"""

from __future__ import annotations

import time
import sys
from typing import Optional, Tuple
from dataclasses import dataclass

# Try to import pyautogui, but handle environments without display
try:
    import pyautogui
    # Configure PyAutoGUI settings for safety
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.05  # Small delay between actions
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
except Exception:
    PYAUTOGUI_AVAILABLE = False


@dataclass
class MousePosition:
    """Represents a mouse position."""
    x: int
    y: int
    timestamp: float = 0
    
    def __post_init__(self):
        if self.timestamp == 0:
            self.timestamp = time.time()


class MouseTool:
    """Tool for controlling mouse cursor and performing mouse actions.
    
    This class wraps PyAutoGUI functionality to provide reliable mouse
    control for the Jarvis agent.
    """
    
    def __init__(self):
        if not PYAUTOGUI_AVAILABLE:
            raise ImportError(
                "pyautogui is required for mouse control. "
                "Install it with: pip install pyautogui"
            )
        self._platform = "unknown"
        
        # Detect platform
        if sys.platform == "darwin":
            self._platform = "macos"
        elif sys.platform == "win32":
            self._platform = "windows"
        else:
            self._platform = "linux"
    
    def move_to(self, x: int, y: int, duration: float = 0) -> None:
        """Move the mouse cursor to the specified position."""
        pyautogui.moveTo(x, y, duration=duration)
    
    def move(self, dx: int, dy: int, duration: float = 0) -> None:
        """Move the mouse cursor by the specified offset."""
        pyautogui.move(dx, dy, duration=duration)
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left", clicks: int = 1, interval: float = 0) -> None:
        """Perform a mouse click."""
        pyautogui.click(x=x, y=y, clicks=clicks, interval=interval, button=button)
    
    def double_click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left") -> None:
        """Perform a double click."""
        pyautogui.doubleClick(x=x, y=y, button=button)
    
    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """Perform a right click (context menu)."""
        pyautogui.rightClick(x=x, y=y)
    
    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """Scroll the mouse wheel."""
        pyautogui.scroll(clicks, x=x, y=y)
    
    def get_position(self) -> MousePosition:
        """Get the current mouse position."""
        x, y = pyautogui.position()
        return MousePosition(x=int(x), y=int(y), timestamp=time.time())
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get the screen dimensions."""
        width, height = pyautogui.size()
        return (int(width), int(height))
    
    # Aliases for common operations
    def left_click(self, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """Perform a left click."""
        self.click(x, y, button="left")
    
    def hover(self, x: int, y: int, duration: float = 0) -> None:
        """Move to position without clicking."""
        self.move_to(x, y, duration=duration)


# Singleton instance
_mouse_tool: Optional[MouseTool] = None


def get_mouse_tool() -> MouseTool:
    """Get or create the singleton mouse tool instance."""
    global _mouse_tool
    if _mouse_tool is None:
        _mouse_tool = MouseTool()
    return _mouse_tool


def get_position() -> MousePosition:
    """Convenience function to get current mouse position."""
    return get_mouse_tool().get_position()


def move_to(x: int, y: int, duration: float = 0) -> None:
    """Convenience function to move mouse to position."""
    get_mouse_tool().move_to(x, y, duration=duration)


def click(x: Optional[int] = None, y: Optional[int] = None) -> None:
    """Convenience function to perform a left click."""
    get_mouse_tool().click(x, y)