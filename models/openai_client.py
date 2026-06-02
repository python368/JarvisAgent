# models/openai_client.py
"""OpenAI API client implementation.

This module provides a complete implementation of the OpenAI chat API client,
extending the base LLM client interface. It supports both standard and streaming
chat completions.
"""

from __future__ import annotations

import os
from typing import List, Dict, Any, AsyncGenerator, Optional

from openai import OpenAI

from models.base_client import LLMClient
from config.app_config import Config


class OpenAIClient(LLMClient):
    """Client for OpenAI chat completions.
    
    Parameters
    ----------
    api_key : str
        OpenAI API key for authentication.
    model : str, optional
        Model name to use for chat completions (default: 'gpt-4o-mini').
    """

    DEFAULT_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    ]

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.model = model
        self._client = OpenAI(api_key=self.api_key)

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def supported_models(self) -> List[str]:
        return self.DEFAULT_MODELS

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send a list of messages to the OpenAI chat endpoint.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            **kwargs: Additional parameters (model override, temperature, etc.)
            
        Returns:
            The assistant's reply as a string.
        """
        model = kwargs.get("model", self.model)
        temperature = kwargs.get("temperature", 0.7)
        
        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    async def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """Send a streaming chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            **kwargs: Additional parameters.
            
        Yields:
            Chunks of the assistant's response as they arrive.
        """
        model = kwargs.get("model", self.model)
        temperature = kwargs.get("temperature", 0.7)
        
        stream = self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def list_models(self) -> List[str]:
        """Return a list of available models for OpenAI.
        
        Returns:
            Sorted list of model identifiers.
        """
        try:
            models = self._client.models.list()
            return sorted([m.id for m in models.data])
        except Exception:
            return self.DEFAULT_MODELS

    def test_connection(self) -> bool:
        """Test the connection to OpenAI API.
        
        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            self._client.models.list()
            return True
        except Exception:
            return False


def get_client(api_key: Optional[str] = None, model: Optional[str] = None) -> OpenAIClient:
    """Factory function to get an OpenAI client instance.
    
    Args:
        api_key: Optional API key override.
        model: Optional model override.
        
    Returns:
        Configured OpenAIClient instance.
    """
    cfg = Config()
    return OpenAIClient(
        api_key=api_key or cfg.get("api_key", ""),
        model=model or cfg.get("model_name", "gpt-4o-mini"),
    )