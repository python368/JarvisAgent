"""Ollama local LLM client implementation.

This module provides a complete implementation for connecting to local Ollama servers,
extending the base LLM client interface. It supports both standard and streaming
chat completions with local models.
"""

from __future__ import annotations

from typing import List, Dict, Any, AsyncGenerator, Optional

import requests

from models.base_client import LLMClient
from config.app_config import Config


class OllamaClient(LLMClient):
    """Client for Ollama's local API.
    
    Parameters
    ----------
    base_url : str
        Base URL of the Ollama server (default: 'http://localhost:11434').
    model : str
        Model name to use for chat completions (default: 'llama2').
    """

    DEFAULT_MODELS = [
        "llama3.2",
        "llama3.2:1b",
        "llama3.1",
        "llama3",
        "llama2",
        "mistral",
        "codellama",
        "phi3",
        "qwen2.5",
        "deepseek-r1",
    ]

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2") -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def supported_models(self) -> List[str]:
        return self.DEFAULT_MODELS

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send a list of messages to Ollama and return the assistant reply.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            **kwargs: Additional parameters (model override, temperature, etc.)
            
        Returns:
            The assistant's reply as a string.
        """
        model = kwargs.get("model", self.model)
        temperature = kwargs.get("temperature", 0.7)
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        
        try:
            resp = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120
            )
            resp.raise_for_status()
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Please ensure Ollama is running."
            )
        except Exception as exc:
            raise RuntimeError(f"Ollama request failed: {exc}")
        
        data = resp.json()
        return data.get("message", {}).get("content", "")

    async def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """Send a streaming chat completion request to Ollama.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            **kwargs: Additional parameters.
            
        Yields:
            Chunks of the assistant's response as they arrive.
        """
        model = kwargs.get("model", self.model)
        temperature = kwargs.get("temperature", 0.7)
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
            }
        }
        
        try:
            resp = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=True,
                timeout=120
            )
            resp.raise_for_status()
        except Exception as exc:
            raise RuntimeError(f"Ollama streaming request failed: {exc}")
        
        for line in resp.iter_lines():
            if line:
                import json
                try:
                    data = json.loads(line)
                    content = data.get("message", {}).get("content", "")
                    if content:
                        yield content
                except json.JSONDecodeError:
                    continue

    def list_models(self) -> List[str]:
        """Return a list of model names available on the Ollama server.
        
        Returns:
            List of model names or default models if server is unreachable.
        """
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return [model.get("name", "") for model in data.get("models", [])]
        except Exception:
            return self.DEFAULT_MODELS

    def test_connection(self) -> bool:
        """Test the connection to the Ollama server.
        
        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False


def get_client(base_url: Optional[str] = None, model: Optional[str] = None) -> OllamaClient:
    """Factory function to get an Ollama client instance.
    
    Args:
        base_url: Optional base URL override.
        model: Optional model override.
        
    Returns:
        Configured OllamaClient instance.
    """
    cfg = Config()
    return OllamaClient(
        base_url=base_url or cfg.get("ollama_url", "http://localhost:11434"),
        model=model or cfg.get("ollama_model", "llama3.2"),
    )
