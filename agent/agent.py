"""Main agent implementation for Jarvis.

This module provides the core ComputerAgent class that orchestrates:
- Vision: Screen observation via screenshots
- Planning: Task decomposition and action planning
- Execution: Computer control (mouse, keyboard, apps)
- Memory: Conversation context and learned knowledge
"""

from __future__ import annotations

import asyncio
import re
import time
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum

from agent.memory import ShortTermMemory, LongTermMemory
from models.model_router import get_client
from tools.screenshot import capture_screen, Screenshot


class AgentState(Enum):
    """Agent execution states."""
    IDLE = "idle"
    OBSERVING = "observing"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING = "waiting"
    ERROR = "error"
    DONE = "done"


@dataclass
class Action:
    """Represents a planned or executed action."""
    action_type: str  # 'click', 'type', 'key_press', 'scroll', 'wait', 'observe'
    params: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    success: bool = False
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class TaskResult:
    """Result of a task execution."""
    success: bool
    message: str
    actions: List[Action] = field(default_factory=list)
    final_state: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0


class ComputerAgent:
    """Main agent for computer control tasks.
    
    The ComputerAgent uses a vision-language model to:
    1. Observe the screen state
    2. Plan actions to accomplish goals
    3. Execute actions via mouse/keyboard
    4. Verify results and adapt
    """
    
    SYSTEM_PROMPT = """You are Jarvis, an AI agent that controls a computer to complete tasks.

Your capabilities:
- Screenshot: Capture the screen to see current state
- Click: Move mouse and click at coordinates
- Type: Type text into focused input fields
- Key Press: Press special keys (Enter, Tab, Escape, etc.)
- Scroll: Scroll up/down
- Wait: Wait for UI to update
- Open App: Launch applications

When given a task:
1. Take a screenshot to see the current state
2. Analyze what needs to be done
3. Plan your first action
4. Execute the action
5. Observe the result
6. Repeat until task is complete

Always be precise with coordinates. Use the screen state to guide your actions."""

    def __init__(self, max_retries: int = 3, max_steps: int = 50):
        """Initialize the computer agent.
        
        Args:
            max_retries: Maximum retries for failed actions.
            max_steps: Maximum steps per task.
        """
        self.max_retries = max_retries
        self.max_steps = max_steps
        self.short_memory = ShortTermMemory(max_messages=50)
        self.long_memory = LongTermMemory()
        self.client = None
        self.state = AgentState.IDLE
        
        # Tool registry
        self._tools = {
            "click": self._tool_click,
            "type": self._tool_type,
            "key_press": self._tool_key_press,
            "scroll": self._tool_scroll,
            "wait": self._tool_wait,
            "open_app": self._tool_open_app,
        }
    
    def _get_client(self):
        """Get or initialize the LLM client."""
        if self.client is None:
            self.client = get_client()
        return self.client
    
    async def execute_task(self, task: str, system_prompt: Optional[str] = None) -> TaskResult:
        """Execute a task end-to-end.
        
        Args:
            task: Task description.
            system_prompt: Optional system prompt override.
            
        Returns:
            TaskResult with execution details.
        """
        start_time = time.time()
        actions = []
        
        # Setup
        self.short_memory.clear()
        prompt = system_prompt or self.SYSTEM_PROMPT
        self.short_memory.add_system_message(prompt)
        self.short_memory.add_user_message(f"TASK: {task}")
        
        step = 0
        last_screenshot = None
        
        while step < self.max_steps:
            step += 1
            self.state = AgentState.OBSERVING
            
            # Capture screenshot
            try:
                last_screenshot = capture_screen()
            except Exception as e:
                actions.append(Action(action_type="screenshot", params={}, success=False, error=str(e)))
            
            # Build context for planning
            messages = self.short_memory.get_messages()
            if last_screenshot:
                # Add screenshot info to last user message
                screenshot_info = f"\n\nSCREENSHOT: {last_screenshot.width}x{last_screenshot.height} image captured"
                if messages and messages[-1]["role"] == "user":
                    messages[-1]["content"] += screenshot_info
            
            # Get next action from LLM
            self.state = AgentState.PLANNING
            try:
                client = self._get_client()
                response = client.chat(messages)
            except Exception as e:
                self.state = AgentState.ERROR
                return TaskResult(
                    success=False,
                    message=f"LLM error: {str(e)}",
                    actions=actions,
                    execution_time=time.time() - start_time,
                )
            
            self.short_memory.add_assistant_message(response)
            
            # Parse and execute action
            action = self._parse_action(response)
            if action is None:
                # No action found, check if task is complete
                if self._is_task_complete(response):
                    return TaskResult(
                        success=True,
                        message="Task completed successfully",
                        actions=actions,
                        execution_time=time.time() - start_time,
                    )
                # Continue conversation
                self.short_memory.add_user_message("Continue with the task. If done, explain what was accomplished.")
                continue
            
            # Execute action
            self.state = AgentState.EXECUTING
            result = await self._execute_action(action)
            actions.append(result)
            
            # Report result
            result_msg = f"Action {action.action_type} "
            if result.success:
                result_msg += f"succeeded. {result.result or ''}"
            else:
                result_msg += f"failed: {result.error}"
            
            self.short_memory.add_user_message(result_msg)
            
            if not result.success and result.action_type != "wait":
                # Retry logic
                if len([a for a in actions if a.action_type == action.action_type]) < self.max_retries:
                    continue
                # Too many retries, give up
                return TaskResult(
                    success=False,
                    message=f"Action {action.action_type} failed after {self.max_retries} retries",
                    actions=actions,
                    execution_time=time.time() - start_time,
                )
        
        # Max steps reached
        return TaskResult(
            success=False,
            message=f"Task not completed after {self.max_steps} steps",
            actions=actions,
            execution_time=time.time() - start_time,
        )
    
    def _parse_action(self, response: str) -> Optional[Action]:
        """Parse action from LLM response.
        
        Expected format: ```action\ntype: click\nparams: x=100, y=200\n```
        """
        # Look for action block
        action_pattern = r"```action\s*\n(.*?)\n```"
        match = re.search(action_pattern, response, re.DOTALL)
        
        if not match:
            # Try simpler patterns
            if "TASK COMPLETE" in response.upper() or "DONE" in response.upper():
                return None  # Task is complete
        
        if not match:
            return None
        
        action_text = match.group(1)
        
        # Parse action type
        type_match = re.search(r"type:\s*(\w+)", action_text)
        if not type_match:
            return None
        
        action_type = type_match.group(1)
        params = {}
        
        # Parse parameters
        params_match = re.search(r"params:\s*(.+?)(?:\n|$)", action_text, re.DOTALL)
        if params_match:
            params_str = params_match.group(1)
            # Parse key=value pairs
            for pair in params_str.split(","):
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    # Try to convert to int
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                    params[key] = value
        
        return Action(action_type=action_type, params=params)
    
    async def _execute_action(self, action: Action) -> Action:
        """Execute a parsed action."""
        tool = self._tools.get(action.action_type)
        
        if tool is None:
            action.success = False
            action.error = f"Unknown action type: {action.action_type}"
            return action
        
        try:
            result = await tool(action.params)
            action.success = True
            action.result = result
        except Exception as e:
            action.success = False
            action.error = str(e)
        
        return action
    
    def _is_task_complete(self, response: str) -> bool:
        """Check if the response indicates task completion."""
        complete_phrases = [
            "task complete", "task completed",
            "done", "finished", "successfully completed",
            "the task has been completed",
        ]
        response_lower = response.lower()
        return any(phrase in response_lower for phrase in complete_phrases)
    
    # Tool implementations
    async def _tool_click(self, params: Dict[str, Any]) -> str:
        """Execute a click action."""
        from tools.mouse import get_mouse_tool
        x = params.get("x")
        y = params.get("y")
        button = params.get("button", "left")
        
        mouse = get_mouse_tool()
        
        if x is not None and y is not None:
            mouse.move_to(x, y)
            await asyncio.sleep(0.1)
            mouse.click(button=button)
        else:
            mouse.click()
        
        await asyncio.sleep(0.2)
        return f"Clicked at ({x}, {y}) with {button} button"
    
    async def _tool_type(self, params: Dict[str, Any]) -> str:
        """Execute a type action."""
        from tools.keyboard import get_keyboard_tool
        text = params.get("text", "")
        
        keyboard = get_keyboard_tool()
        keyboard.typewrite(text, interval=0.01)
        
        await asyncio.sleep(0.1)
        return f"Typed: {text[:50]}{'...' if len(text) > 50 else ''}"
    
    async def _tool_key_press(self, params: Dict[str, Any]) -> str:
        """Execute a key press action."""
        from tools.keyboard import get_keyboard_tool
        key = params.get("key", "enter")
        
        keyboard = get_keyboard_tool()
        keyboard.press(key)
        
        await asyncio.sleep(0.1)
        return f"Pressed key: {key}"
    
    async def _tool_scroll(self, params: Dict[str, Any]) -> str:
        """Execute a scroll action."""
        from tools.mouse import get_mouse_tool
        clicks = params.get("clicks", 3)
        direction = params.get("direction", "down")
        
        mouse = get_mouse_tool()
        if direction == "up":
            mouse.scroll(clicks)
        else:
            mouse.scroll(-clicks)
        
        await asyncio.sleep(0.2)
        return f"Scrolled {direction} {clicks} clicks"
    
    async def _tool_wait(self, params: Dict[str, Any]) -> str:
        """Wait action."""
        seconds = params.get("seconds", 1)
        await asyncio.sleep(seconds)
        return f"Waited {seconds} seconds"
    
    async def _tool_open_app(self, params: Dict[str, Any]) -> str:
        """Open an application."""
        from tools.app_control import get_app_tool
        app_name = params.get("name") or params.get("app", "")
        
        if not app_name:
            return "No app name provided"
        
        tool = get_app_tool()
        
        if self._is_url(app_name):
            tool.open_url(app_name)
        else:
            tool.launch_app(app_name)
        
        await asyncio.sleep(1)
        return f"Opened: {app_name}"
    
    def _is_url(self, text: str) -> bool:
        return text.startswith("http://") or text.startswith("https://")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history."""
        return self.short_memory.get_messages()
    
    def reset(self) -> None:
        """Reset the agent state."""
        self.short_memory.clear()
        self.state = AgentState.IDLE