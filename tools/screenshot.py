"""Screenshot tool for capturing screen content.

This module provides screenshot functionality for the Jarvis agent to observe
the current state of the computer screen. It supports full screen capture,
region capture, and various image formats.
"""

from __future__ import annotations

import io
import time
from typing import Optional, Tuple
from dataclasses import dataclass

try:
    import mss
    from PIL import Image
    
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False


@dataclass
class Screenshot:
    """Represents a screenshot with metadata."""
    image: "Image.Image"
    width: int
    height: int
    timestamp: float
    monitor: int = 0
    
    def to_bytes(self, fmt: str = "PNG") -> bytes:
        """Convert screenshot to bytes."""
        buffer = io.BytesIO()
        self.image.save(buffer, format=fmt)
        return buffer.getvalue()
    
    def to_base64(self, fmt: str = "PNG") -> str:
        """Convert screenshot to base64 string for API transmission."""
        import base64
        return base64.b64encode(self.to_bytes(fmt)).decode("utf-8")
    
    def save(self, path: str, img_format: Optional[str] = None) -> None:
        """Save screenshot to file."""
        if img_format is None:
            img_format = path.rsplit(".", 1)[-1].upper() if "." in path else "PNG"
        self.image.save(path, format=img_format)


class ScreenshotTool:
    """Tool for capturing screenshots of the computer screen."""
    
    def __init__(self):
        if not MSS_AVAILABLE:
            raise ImportError("mss and Pillow are required for screenshots. Install: pip install mss Pillow")
        self._sct = mss.mss()
        self._monitor_count = len(self._sct.monitors)
    
    def capture_full_screen(self, monitor: int = 1) -> Screenshot:
        """Capture the full screen.
        
        Args:
            monitor: Monitor index (1+ = specific monitor, 0 = all monitors).
        """
        if monitor == 0:
            monitor_spec = self._sct.monitors[0]
        else:
            monitor_spec = self._sct.monitors[min(monitor, self._monitor_count)]
        
        screenshot = self._sct.grab(monitor_spec)
        image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        
        return Screenshot(
            image=image,
            width=image.width,
            height=image.height,
            timestamp=time.time(),
            monitor=monitor,
        )
    
    def capture_region(self, x: int, y: int, width: int, height: int, monitor: int = 1) -> Screenshot:
        """Capture a specific region of the screen."""
        region = {"left": x, "top": y, "width": width, "height": height}
        screenshot = self._sct.grab(region)
        image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        
        return Screenshot(
            image=image,
            width=image.width,
            height=image.height,
            timestamp=time.time(),
            monitor=monitor,
        )
    
    def get_monitors(self) -> list[dict]:
        """Get information about connected monitors."""
        return [
            {"index": i, "left": m.get("left", 0), "top": m.get("top", 0),
             "width": m.get("width", 0), "height": m.get("height", 0)}
            for i, m in enumerate(self._sct.monitors)
        ]
    
    def close(self) -> None:
        """Clean up resources."""
        if hasattr(self, "_sct"):
            self._sct.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Singleton instance
_screenshot_tool: Optional[ScreenshotTool] = None


def get_screenshot_tool() -> ScreenshotTool:
    """Get or create the singleton screenshot tool instance."""
    global _screenshot_tool
    if _screenshot_tool is None:
        _screenshot_tool = ScreenshotTool()
    return _screenshot_tool


def capture_screen(region: Optional[Tuple[int, int, int, int]] = None) -> Screenshot:
    """Convenience function to capture the screen.
    
    Args:
        region: Optional (x, y, width, height) to capture specific region.
    """
    tool = get_screenshot_tool()
    if region:
        x, y, w, h = region
        return tool.capture_region(x, y, w, h)
    return tool.capture_full_screen()