# models/anthropic_client.py
"""Anthropic Claude API client implementation.

This module provides a complete implementation of the Anthropic Claude API client,
extending the base LLM client interface. It supports both standard and streaming
chat completions.
"""

from __future__ import annotations

import os
from typing import List, Dict, Any, AsyncGenerator, Optional

from anthropic import Anthropic

from models.base_client import LLMClient
from config.app_config import Config


class AnthropicClient(LLMClient):
    """Client for Anthropic Claude chat completions.
    
    Parameters
    ----------
    api_key : str
        Anthropic API key for authentication.
    model : str, optional
        Model name to use for chat completions (default: 'claude-3-5-sonnet-20241022').
    """

    DEFAULT_MODELS = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620",
        "claude-3-opus-20240229",
        "claude-3-haiku-20240307",
    ]

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022") -> None:
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.model = model
        self._client = Anthropic(api_key=self.api_key)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def supported_models(self) -> List[str]:
        return self.DEFAULT_MODELS

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send a list of messages to the Anthropic Claude API.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            The assistant's reply as a string.
        """
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 4096)
        
        # Convert messages format for Anthropic
        # Anthropic uses 'user' and 'assistant' roles
        anthropic_messages = []
        system = None
        
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            elif msg["role"] in ("user", "assistant"):
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        response = self._client.messages.create(
            model=self.model,
            messages=anthropic_messages,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return response.content[0].text if response.content else ""

    async def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """Send a streaming chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            **kwargs: Additional parameters.
            
        Yields:
            Chunks of the assistant's response as they arrive.
        """
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 4096)
        
        # Convert messages format for Anthropic
        anthropic_messages = []
        system = None
        
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            elif msg["role"] in ("user", "assistant"):
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        with self._client.messages.stream(
            model=self.model,
            messages=anthropic_messages,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
        ) as stream:
            for text in stream.text_stream:
                yield text

    def list_models(self) -> List[str]:
        """Return a list of available models for Anthropic.
        
        Returns:
            List of model identifiers.
        """
        return self.DEFAULT_MODELS

    def test_connection(self) -> bool:
        """Test the connection to Anthropic API.
        
        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            self._client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
            )
            return True
        except Exception:
            return False


def get_client(api_key: Optional[str] = None, model: Optional[str] = None) -> AnthropicClient:
    """Factory function to get an Anthropic client instance.
    
    Args:
        api_key: Optional API key override.
        model: Optional model override.
        
    Returns:
        Configured AnthropicClient instance.
    """
    cfg = Config()
    return AnthropicClient(
        api_key=api_key or cfg.get("anthropic_api_key", ""),
        model=model or cfg.get("anthropic_model", "claude-3-5-sonnet-20241022"),
    )