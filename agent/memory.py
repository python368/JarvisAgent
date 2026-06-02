"""Agent memory system for maintaining conversation context.

This module provides memory implementations for the agent:
- ShortTermMemory: Current conversation context
- LongTermMemory: Persistent storage across sessions
"""

from __future__ import annotations

import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Message:
    """Represents a message in the conversation."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {"role": self.role, "content": self.content, "timestamp": self.timestamp, "metadata": self.metadata}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(role=data.get("role", "user"), content=data.get("content", ""),
                   timestamp=data.get("timestamp", time.time()), metadata=data.get("metadata", {}))


class ShortTermMemory:
    """Short-term memory for current conversation context."""
    
    def __init__(self, max_messages: int = 100):
        self.max_messages = max_messages
        self._messages: List[Message] = []
        self._system_prompt: Optional[str] = None
    
    def add_message(self, role: str, content: str, **metadata) -> None:
        self._messages.append(Message(role=role, content=content, metadata=metadata))
        self._prune()
    
    def add_user_message(self, content: str) -> None:
        self.add_message("user", content)
    
    def add_assistant_message(self, content: str) -> None:
        self.add_message("assistant", content)
    
    def add_system_message(self, content: str) -> None:
        self._system_prompt = content
        self._messages = [m for m in self._messages if m.role != "system"]
        self._messages.insert(0, Message(role="system", content=content))
    
    def get_messages(self) -> List[Dict[str, str]]:
        return [{"role": m.role, "content": m.content} for m in self._messages]
    
    def get_last_n(self, n: int) -> List[Message]:
        return self._messages[-n:] if n > 0 else self._messages
    
    def clear(self) -> None:
        self._messages = []
        if self._system_prompt:
            self._messages.append(Message(role="system", content=self._system_prompt))
    
    def _prune(self) -> None:
        system_messages = [m for m in self._messages if m.role == "system"]
        other_messages = [m for m in self._messages if m.role != "system"]
        if len(other_messages) > self.max_messages:
            other_messages = other_messages[-self.max_messages:]
        self._messages = system_messages + other_messages
    
    def __len__(self) -> int:
        return len(self._messages)


class LongTermMemory:
    """Long-term memory for persistent storage across sessions."""
    
    def __init__(self, storage_path: str = "config/long_term_memory.json"):
        self.storage_path = storage_path
        self._data: Dict[str, Any] = {
            "user_preferences": {}, "learned_facts": [], "task_history": [],
            "interaction_count": 0, "last_updated": None,
        }
        self._load()
    
    def _load(self) -> None:
        import os
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                pass
    
    def _save(self) -> None:
        import os
        from datetime import datetime
        self._data["last_updated"] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
    def set_preference(self, key: str, value: Any) -> None:
        self._data["user_preferences"][key] = value
        self._save()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        return self._data["user_preferences"].get(key, default)
    
    def add_fact(self, fact: str, category: str = "general") -> None:
        self._data["learned_facts"].append({"fact": fact, "category": category, "timestamp": time.time()})
        self._save()
    
    def get_facts(self, category: Optional[str] = None) -> List[Dict]:
        if category:
            return [f for f in self._data["learned_facts"] if f.get("category") == category]
        return self._data["learned_facts"]
    
    def record_task(self, task: str, success: bool, details: Optional[Dict] = None) -> None:
        self._data["task_history"].append({"task": task, "success": success, "details": details or {}, "timestamp": time.time()})
        self._data["interaction_count"] = self._data.get("interaction_count", 0) + 1
        self._save()
    
    def get_task_history(self, limit: int = 50) -> List[Dict]:
        return self._data["task_history"][-limit:]
    
    def clear(self) -> None:
        self._data = {"user_preferences": {}, "learned_facts": [], "task_history": [], "interaction_count": 0, "last_updated": None}
        self._save()