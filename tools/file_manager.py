"""File management tool for file operations.

This module provides file system operations for the Jarvis agent,
including reading, writing, copying, moving, and searching files.
"""

from __future__ import annotations

import os
import shutil
import glob as glob_module
from pathlib import Path
from typing import Optional, List, Union


class FileManagerTool:
    """Tool for file system operations.
    
    This class provides safe and controlled file system access for the Jarvis agent.
    """
    
    def __init__(self):
        """Initialize the file manager."""
        self._home = Path.home()
    
    def read_file(self, path: Union[str, Path]) -> str:
        """Read the contents of a file.
        
        Args:
            path: Path to the file.
            
        Returns:
            File contents as string.
            
        Raises:
            FileNotFoundError: If file doesn't exist.
        """
        path = Path(path).expanduser()
        return path.read_text(encoding="utf-8")
    
    def write_file(self, path: Union[str, Path], content: str) -> bool:
        """Write content to a file.
        
        Args:
            path: Path to the file.
            content: Content to write.
            
        Returns:
            True if successful.
        """
        try:
            path = Path(path).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return True
        except Exception:
            return False
    
    def append_file(self, path: Union[str, Path], content: str) -> bool:
        """Append content to a file.
        
        Args:
            path: Path to the file.
            content: Content to append.
            
        Returns:
            True if successful.
        """
        try:
            path = Path(path).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception:
            return False
    
    def copy_file(self, src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """Copy a file.
        
        Args:
            src: Source path.
            dst: Destination path.
            
        Returns:
            True if successful.
        """
        try:
            src = Path(src).expanduser()
            dst = Path(dst).expanduser()
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            return True
        except Exception:
            return False
    
    def move_file(self, src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """Move a file.
        
        Args:
            src: Source path.
            dst: Destination path.
            
        Returns:
            True if successful.
        """
        try:
            src = Path(src).expanduser()
            dst = Path(dst).expanduser()
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            return True
        except Exception:
            return False
    
    def delete_file(self, path: Union[str, Path]) -> bool:
        """Delete a file.
        
        Args:
            path: Path to the file.
            
        Returns:
            True if successful.
        """
        try:
            path = Path(path).expanduser()
            path.unlink()
            return True
        except Exception:
            return False
    
    def exists(self, path: Union[str, Path]) -> bool:
        """Check if a path exists.
        
        Args:
            path: Path to check.
            
        Returns:
            True if exists.
        """
        return Path(path).expanduser().exists()
    
    def is_file(self, path: Union[str, Path]) -> bool:
        """Check if path is a file.
        
        Args:
            path: Path to check.
            
        Returns:
            True if it's a file.
        """
        return Path(path).expanduser().is_file()
    
    def is_dir(self, path: Union[str, Path]) -> bool:
        """Check if path is a directory.
        
        Args:
            path: Path to check.
            
        Returns:
            True if it's a directory.
        """
        return Path(path).expanduser().is_dir()
    
    def list_dir(
        self,
        path: Union[str, Path] = ".",
        pattern: Optional[str] = None,
        recursive: bool = False
    ) -> List[str]:
        """List directory contents.
        
        Args:
            path: Directory to list.
            pattern: Optional glob pattern.
            recursive: Whether to recurse into subdirectories.
            
        Returns:
            List of file/directory names.
        """
        path = Path(path).expanduser()
        
        if not path.exists():
            return []
        
        if pattern:
            if recursive:
                return [str(p) for p in path.rglob(pattern)]
            return [str(p) for p in path.glob(pattern)]
        
        if recursive:
            return [str(p) for p in path.rglob("*")]
        return [str(p) for p in path.iterdir()]
    
    def create_dir(self, path: Union[str, Path]) -> bool:
        """Create a directory.
        
        Args:
            path: Directory path to create.
            
        Returns:
            True if successful.
        """
        try:
            Path(path).expanduser().mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
    
    def delete_dir(self, path: Union[str, Path], recursive: bool = False) -> bool:
        """Delete a directory.
        
        Args:
            path: Directory path to delete.
            recursive: Whether to delete recursively.
            
        Returns:
            True if successful.
        """
        try:
            path = Path(path).expanduser()
            if recursive:
                shutil.rmtree(path)
            else:
                path.rmdir()
            return True
        except Exception:
            return False
    
    def get_file_size(self, path: Union[str, Path]) -> int:
        """Get file size in bytes.
        
        Args:
            path: File path.
            
        Returns:
            File size in bytes.
        """
        try:
            return Path(path).expanduser().stat().st_size
        except Exception:
            return 0
    
    def get_modified_time(self, path: Union[str, Path]) -> float:
        """Get file modification time.
        
        Args:
            path: File path.
            
        Returns:
            Modification timestamp.
        """
        try:
            return Path(path).expanduser().stat().st_mtime
        except Exception:
            return 0
    
    def search(self, path: Union[str, Path], text: str, recursive: bool = True) -> List[str]:
        """Search for text in files.
        
        Args:
            path: Directory to search in.
            text: Text to search for.
            recursive: Whether to search recursively.
            
        Returns:
            List of file paths containing the text.
        """
        matches = []
        path = Path(path).expanduser()
        
        if not path.exists():
            return matches
        
        pattern = "**/*" if recursive else "*"
        
        for file_path in path.glob(pattern):
            if file_path.is_file():
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    if text.lower() in content.lower():
                        matches.append(str(file_path))
                except Exception:
                    pass
        
        return matches
    
    def get_home_dir(self) -> str:
        """Get the user's home directory.
        
        Returns:
            Home directory path.
        """
        return str(self._home)
    
    def normalize_path(self, path: Union[str, Path]) -> str:
        """Normalize a path (expand user, resolve symlinks).
        
        Args:
            path: Path to normalize.
            
        Returns:
            Normalized path string.
        """
        return str(Path(path).expanduser().resolve())


# Singleton instance
_file_tool: Optional[FileManagerTool] = None


def get_file_tool() -> FileManagerTool:
    """Get or create the singleton file manager instance."""
    global _file_tool
    if _file_tool is None:
        _file_tool = FileManagerTool()
    return _file_tool