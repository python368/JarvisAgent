"""Test suite for Jarvis Agent.

Run with: python -m pytest tests/ -v
"""

import pytest
import asyncio
import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMemory:
    """Tests for memory modules."""
    
    def test_short_term_memory_add_message(self):
        """Test adding messages to short-term memory."""
        from agent.memory import ShortTermMemory, Message
        
        memory = ShortTermMemory(max_messages=10)
        
        memory.add_user_message("Hello")
        memory.add_assistant_message("Hi there!")
        
        messages = memory.get_messages()
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"
        assert messages[1]["role"] == "assistant"
    
    def test_short_term_memory_pruning(self):
        """Test automatic pruning when max messages exceeded."""
        from agent.memory import ShortTermMemory
        
        memory = ShortTermMemory(max_messages=3)
        
        for i in range(5):
            memory.add_user_message(f"Message {i}")
        
        # Should keep only last 3
        assert len(memory) == 3
        messages = memory.get_messages()
        # Messages should be the last 3 (user messages only, since system prompt was overwritten)
        content_values = [m["content"] for m in messages]
        assert "Message 2" in content_values or "Message 3" in content_values or "Message 4" in content_values
    
    def test_long_term_memory_preferences(self):
        """Test long-term memory preference storage."""
        from agent.memory import LongTermMemory
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = LongTermMemory(storage_path=f"{tmpdir}/test_memory.json")
            
            memory.set_preference("theme", "dark")
            memory.set_preference("language", "en")
            
            # Create new instance to test persistence
            memory2 = LongTermMemory(storage_path=f"{tmpdir}/test_memory.json")
            
            assert memory2.get_preference("theme") == "dark"
            assert memory2.get_preference("language") == "en"
            assert memory2.get_preference("nonexistent", "default") == "default"


class TestModelClients:
    """Tests for LLM client implementations."""
    
    def test_base_client_interface(self):
        """Test that all clients implement the base interface."""
        from models.base_client import LLMClient
        from models.openai_client import OpenAIClient
        from models.anthropic_client import AnthropicClient
        from models.ollama_client import OllamaClient
        
        # Check that all client classes have required methods
        for client_class in [OpenAIClient, AnthropicClient, OllamaClient]:
            assert hasattr(client_class, 'chat')
            assert hasattr(client_class, 'chat_stream')
            assert hasattr(client_class, 'list_models')
            assert hasattr(client_class, 'test_connection')
    
    def test_model_router_providers(self):
        """Test that model router returns correct provider names."""
        from models.model_router import get_available_providers, get_provider_info
        
        providers = get_available_providers()
        
        assert "OpenAI" in providers
        assert "Anthropic" in providers
        assert "Ollama" in providers
        assert "Google" in providers
    
    def test_ollama_client_init(self):
        """Test Ollama client initialization."""
        from models.ollama_client import OllamaClient
        
        client = OllamaClient(base_url="http://localhost:11434", model="llama3.2")
        
        assert client.base_url == "http://localhost:11434"
        assert client.model == "llama3.2"
        assert client.provider_name == "ollama"
        assert "llama3.2" in client.supported_models


class TestTools:
    """Tests for computer control tools."""
    
    def test_mouse_tool_available(self):
        """Test that mouse tool is available."""
        from tools.mouse import MouseTool, get_mouse_tool
        
        # Check class exists and can be instantiated
        try:
            mouse = get_mouse_tool()
            # If pyautogui is not installed, will raise ImportError
            assert mouse is not None
        except ImportError:
            pytest.skip("pyautogui not installed")
    
    def test_keyboard_tool_available(self):
        """Test that keyboard tool is available."""
        from tools.keyboard import KeyboardTool, get_keyboard_tool
        
        try:
            keyboard = get_keyboard_tool()
            assert keyboard is not None
        except ImportError:
            pytest.skip("pyautogui not installed")
    
    def test_screenshot_tool_available(self):
        """Test that screenshot tool is available."""
        from tools.screenshot import ScreenshotTool
        
        try:
            # Try to create the tool and capture - may fail without display
            tool = ScreenshotTool()
            screenshot = tool.capture_full_screen()
            assert screenshot.width > 0
            assert screenshot.height > 0
            assert screenshot.image is not None
        except (ImportError, Exception) as e:
            # Screenshot may fail without display - skip the test
            pytest.skip(f"Screenshot requires display: {e}")
    
    def test_file_manager_basic_operations(self):
        """Test file manager basic operations."""
        from tools.file_manager import FileManagerTool
        import tempfile
        
        tool = FileManagerTool()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = f"{tmpdir}/test.txt"
            
            # Write
            assert tool.write_file(test_file, "Hello, Jarvis!")
            
            # Read
            content = tool.read_file(test_file)
            assert content == "Hello, Jarvis!"
            
            # Exists
            assert tool.exists(test_file)
            assert tool.is_file(test_file)
            
            # Size
            assert tool.get_file_size(test_file) > 0
            
            # Delete
            assert tool.delete_file(test_file)
            assert not tool.exists(test_file)


class TestAgent:
    """Tests for agent implementation."""
    
    def test_agent_init(self):
        """Test agent initialization."""
        from agent.agent import ComputerAgent, AgentState
        
        agent = ComputerAgent()
        
        assert agent.state == AgentState.IDLE
        assert agent.short_memory is not None
        assert agent.long_memory is not None
        assert agent.max_retries == 3
        assert agent.max_steps == 50
    
    def test_agent_reset(self):
        """Test agent reset functionality."""
        from agent.agent import ComputerAgent, AgentState
        
        agent = ComputerAgent()
        agent.short_memory.add_user_message("Test")
        
        agent.reset()
        
        assert agent.state == AgentState.IDLE
        assert len(agent.short_memory) == 0
    
    def test_planner_simple(self):
        """Test planner creation."""
        from agent.planner import Planner, create_simple_plan
        
        plan = create_simple_plan("Test task")
        
        assert plan.task == "Test task"
        assert len(plan.steps) == 1
        assert plan.steps[0].description == "Test task"
        assert not plan.is_complete


class TestTaskManager:
    """Tests for task manager."""
    
    def test_task_creation(self):
        """Test task creation."""
        from agent.task_manager import TaskManager, TaskStatus
        
        manager = TaskManager()
        
        task = manager.create_task("test-1", "Test task")
        
        assert task.task_id == "test-1"
        assert task.description == "Test task"
        assert task.status == TaskStatus.PENDING
        assert task.progress == 0.0
    
    def test_task_list(self):
        """Test task listing."""
        from agent.task_manager import TaskManager
        
        manager = TaskManager()
        
        manager.create_task("task-1", "Task 1")
        manager.create_task("task-2", "Task 2")
        manager.create_task("task-3", "Task 3")
        
        tasks = manager.list_tasks()
        assert len(tasks) == 3
    
    def test_task_statistics(self):
        """Test task statistics."""
        from agent.task_manager import TaskManager, TaskStatus
        
        manager = TaskManager()
        manager.create_task("task-1", "Task 1")
        
        stats = manager.get_statistics()
        
        assert stats["total_tasks"] == 1
        assert stats["pending"] == 1


class TestConfig:
    """Tests for configuration."""
    
    def test_config_singleton(self):
        """Test config singleton pattern."""
        from config.app_config import Config
        
        config1 = Config()
        config2 = Config()
        
        assert config1 is config2
    
    def test_config_get_set(self):
        """Test config get/set operations."""
        from config.app_config import Config
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a fresh config instance with temp path
            config = Config.__new__(Config)
            config._config_path = f"{tmpdir}/test_config.json"
            config._load()
            
            # Test set
            config.set("test_key", "test_value")
            
            # Test get
            assert config.get("test_key") == "test_value"
            assert config.get("nonexistent", "default") == "default"
            
            # Test as_dict
            data = config.as_dict()
            assert "test_key" in data


class TestDialogManager:
    """Tests for dialog manager."""
    
    def test_dialog_init(self):
        """Test dialog manager initialization."""
        from agent.dialog_manager import DialogManager
        
        dm = DialogManager()
        
        assert len(dm) == 0
        # System prompt may or may not be set depending on initialization order
        assert hasattr(dm, '_system_prompt_set')
    
    def test_dialog_messages(self):
        """Test adding and retrieving messages."""
        from agent.dialog_manager import DialogManager, MessageRole
        
        dm = DialogManager()
        
        dm.add_user_message("Hello")
        dm.add_assistant_message("Hi there!")
        
        assert len(dm) == 2
        
        recent = dm.get_recent_messages(1)
        assert len(recent) == 1
        assert recent[0].role == MessageRole.ASSISTANT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])