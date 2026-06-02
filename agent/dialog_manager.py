"""Dialog management module for conversational interaction.

This module handles conversation flow, user interactions,
and response generation for the Jarvis agent.
"""

from __future__ import annotations

import time
from typing import List, Dict, Any, Optional, Callable, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum

from agent.memory import ShortTermMemory, LongTermMemory


class MessageRole(Enum):
    """Message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


@dataclass
class DialogMessage:
    """Represents a dialog message."""
    role: MessageRole
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DialogManager:
    """Manages conversational dialog with the user.
    
    This class handles:
    - Message history management
    - Context preservation
    - Response formatting
    - Multi-turn conversations
    """
    
    DEFAULT_SYSTEM_PROMPT = """You are Jarvis, an AI assistant that helps users accomplish tasks on their computer.

You can:
- Control mouse and keyboard to interact with applications
- Take screenshots to see the screen state
- Read and write files
- Launch and manage applications
- Execute complex multi-step tasks autonomously

Be helpful, precise, and explain what you're doing.
When performing actions, briefly describe them.
If something goes wrong, explain the issue and suggest alternatives."""
    
    def __init__(self):
        self.short_memory = ShortTermMemory(max_messages=100)
        self.long_memory = LongTermMemory()
        self.messages: List[DialogMessage] = []
        self._system_prompt_set = False
    
    def reset(self) -> None:
        """Reset the dialog state."""
        self.short_memory.clear()
        self.messages = []
        self._system_prompt_set = False
        self.set_system_prompt(self.DEFAULT_SYSTEM_PROMPT)
    
    def set_system_prompt(self, prompt: str) -> None:
        """Set the system prompt."""
        self.short_memory.add_system_message(prompt)
        self._system_prompt_set = True
    
    def add_user_message(self, content: str, **metadata) -> DialogMessage:
        """Add a user message."""
        msg = DialogMessage(role=MessageRole.USER, content=content, metadata=metadata)
        self.messages.append(msg)
        self.short_memory.add_user_message(content)
        return msg
    
    def add_assistant_message(self, content: str, **metadata) -> DialogMessage:
        """Add an assistant message."""
        msg = DialogMessage(role=MessageRole.ASSISTANT, content=content, metadata=metadata)
        self.messages.append(msg)
        self.short_memory.add_assistant_message(content)
        return msg
    
    def add_tool_message(self, content: str, tool_name: str = "", **metadata) -> DialogMessage:
        """Add a tool result message."""
        metadata = {**metadata, "tool_name": tool_name}
        msg = DialogMessage(role=MessageRole.TOOL, content=content, metadata=metadata)
        self.messages.append(msg)
        return msg
    
    def get_conversation_for_api(self) -> List[Dict[str, str]]:
        """Get messages formatted for API calls."""
        return self.short_memory.get_messages()
    
    def get_recent_messages(self, count: int = 10) -> List[DialogMessage]:
        """Get the most recent messages."""
        return self.messages[-count:] if count > 0 else self.messages
    
    def get_full_context(self, max_tokens: int = 8000) -> str:
        """Get a full context string for the conversation."""
        lines = []
        for msg in self.messages:
            prefix = {
                MessageRole.USER: "User",
                MessageRole.ASSISTANT: "Assistant",
                MessageRole.SYSTEM: "System",
                MessageRole.TOOL: "Tool",
            }.get(msg.role, "Unknown")
            lines.append(f"{prefix}: {msg.content}")
        return "\n\n".join(lines)
    
    def summarize_if_needed(self, llm_client) -> bool:
        """Summarize conversation if it's too long.
        
        Args:
            llm_client: LLM client for summarization.
            
        Returns:
            True if summarization was performed.
        """
        if len(self.messages) > 50:
            # Keep system prompt and last 10 messages
            system_messages = [m for m in self.messages if m.role == MessageRole.SYSTEM]
            recent = self.messages[-10:]
            
            # Create summary prompt
            summary_request = "Summarize the following conversation, keeping key points and user preferences:\n\n"
            for msg in self.messages[:-10]:
                role_name = msg.role.value
                summary_request += f"{role_name}: {msg.content[:200]}\n"
            
            try:
                summary = llm_client.chat([{"role": "user", "content": summary_request}])
                
                # Reset and add summary
                self.messages = system_messages + [
                    DialogMessage(
                        role=MessageRole.SYSTEM,
                        content=f"Previous conversation summary: {summary}"
                    )
                ] + recent
                
                self.short_memory.clear()
                for msg in self.messages:
                    self.short_memory.add_message(msg.role.value, msg.content)
                
                return True
            except Exception:
                return False
        
        return False
    
    def __len__(self) -> int:
        """Get number of messages."""
        return len(self.messages)


# Singleton instance
_dialog_manager: Optional[DialogManager] = None


def get_dialog_manager() -> DialogManager:
    """Get or create the singleton dialog manager."""
    global _dialog_manager
    if _dialog_manager is None:
        _dialog_manager = DialogManager()
    return _dialog_manager