"""Task management module for the Jarvis agent.

This module provides task tracking, execution management, and 
progress monitoring for long-running tasks.
"""

from __future__ import annotations

import time
import asyncio
from typing import List, Dict, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents a task to be executed."""
    task_id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    error: Optional[str] = None
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> float:
        """Get task duration in seconds."""
        if self.started_at is None:
            return 0
        end = self.completed_at or time.time()
        return end - self.started_at
    
    @property
    def is_running(self) -> bool:
        return self.status == TaskStatus.RUNNING
    
    @property
    def is_done(self) -> bool:
        return self.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)


class TaskManager:
    """Manages task execution and tracking.
    
    This class provides:
    - Task creation and tracking
    - Progress monitoring
    - Cancellation support
    - Task history
    """
    
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._current_task: Optional[str] = None
        self._history: List[Task] = []
        self._max_history = 100
        self._cancellation_event: Optional[asyncio.Event] = None
    
    def create_task(self, task_id: str, description: str, **metadata) -> Task:
        """Create a new task.
        
        Args:
            task_id: Unique task identifier.
            description: Task description.
            **metadata: Additional task metadata.
            
        Returns:
            Created Task object.
        """
        task = Task(task_id=task_id, description=description, metadata=metadata)
        self._tasks[task_id] = task
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID.
        
        Args:
            task_id: Task identifier.
            
        Returns:
            Task object or None.
        """
        return self._tasks.get(task_id)
    
    def get_current_task(self) -> Optional[Task]:
        """Get the currently executing task.
        
        Returns:
            Current task or None.
        """
        if self._current_task:
            return self._tasks.get(self._current_task)
        return None
    
    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """List all tasks, optionally filtered by status.
        
        Args:
            status: Optional status filter.
            
        Returns:
            List of tasks.
        """
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)
    
    async def execute_task(
        self,
        task_id: str,
        executor: Callable[[Task], Awaitable[Any]],
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Task:
        """Execute a task with the given executor.
        
        Args:
            task_id: Task identifier.
            executor: Async function that executes the task.
            progress_callback: Optional callback for progress updates.
            
        Returns:
            Completed Task object.
        """
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        self._current_task = task_id
        self._cancellation_event = asyncio.Event()
        
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        
        try:
            if asyncio.iscoroutinefunction(executor):
                result = await asyncio.wait_for(
                    executor(task),
                    timeout=task.metadata.get("timeout", 600)
                )
            else:
                result = executor(task)
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.progress = 1.0
            
        except asyncio.TimeoutError:
            task.status = TaskStatus.FAILED
            task.error = "Task timed out"
        except asyncio.CancelledError:
            task.status = TaskStatus.CANCELLED
            task.error = "Task was cancelled"
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
        finally:
            task.completed_at = time.time()
            self._current_task = None
            self._add_to_history(task)
        
        return task
    
    def update_progress(self, task_id: str, progress: float, message: str = "") -> None:
        """Update task progress.
        
        Args:
            task_id: Task identifier.
            progress: Progress value (0.0 to 1.0).
            message: Optional progress message.
        """
        task = self._tasks.get(task_id)
        if task:
            task.progress = max(0.0, min(1.0, progress))
            if message:
                task.metadata["progress_message"] = message
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task.
        
        Args:
            task_id: Task identifier.
            
        Returns:
            True if cancellation was initiated.
        """
        task = self._tasks.get(task_id)
        if task and task.is_running and self._cancellation_event:
            self._cancellation_event.set()
            return True
        return False
    
    def cancel_all(self) -> int:
        """Cancel all running tasks.
        
        Returns:
            Number of tasks cancelled.
        """
        cancelled = 0
        for task in self._tasks.values():
            if task.is_running:
                self.cancel_task(task.task_id)
                cancelled += 1
        return cancelled
    
    def pause_task(self, task_id: str) -> bool:
        """Pause a running task.
        
        Args:
            task_id: Task identifier.
            
        Returns:
            True if pause was initiated.
        """
        task = self._tasks.get(task_id)
        if task and task.is_running:
            task.status = TaskStatus.PAUSED
            return True
        return False
    
    def resume_task(self, task_id: str) -> bool:
        """Resume a paused task.
        
        Args:
            task_id: Task identifier.
            
        Returns:
            True if resume was successful.
        """
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.PAUSED:
            task.status = TaskStatus.RUNNING
            return True
        return False
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task.
        
        Args:
            task_id: Task identifier.
            
        Returns:
            True if task was deleted.
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False
    
    def get_history(self, limit: int = 50) -> List[Task]:
        """Get task execution history.
        
        Args:
            limit: Maximum number of entries.
            
        Returns:
            List of completed tasks.
        """
        return self._history[:limit]
    
    def clear_history(self) -> None:
        """Clear task history."""
        self._history = []
    
    def _add_to_history(self, task: Task) -> None:
        """Add completed task to history."""
        self._history.insert(0, task)
        if len(self._history) > self._max_history:
            self._history = self._history[:self._max_history]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get task execution statistics.
        
        Returns:
            Dictionary with statistics.
        """
        tasks = list(self._tasks.values())
        history = self._history
        
        return {
            "total_tasks": len(tasks),
            "pending": len([t for t in tasks if t.status == TaskStatus.PENDING]),
            "running": len([t for t in tasks if t.is_running]),
            "completed": len([t for t in history if t.status == TaskStatus.COMPLETED]),
            "failed": len([t for t in history if t.status == TaskStatus.FAILED]),
            "cancelled": len([t for t in history if t.status == TaskStatus.CANCELLED]),
            "average_duration": sum(t.duration for t in history) / len(history) if history else 0,
        }


# Singleton instance
_task_manager: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    """Get or create the singleton task manager instance."""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager