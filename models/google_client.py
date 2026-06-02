
"""Google Gemini API client implementation.

This module provides a complete implementation for the Google Gemini API,
extending the base LLM client interface. It supports both standard and streaming
chat completions.
"""

from __future__ import annotations

import os
from typing import List, Dict, Any, AsyncGenerator, Optional

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from models.base_client import LLMClient
from config.app_config import Config


class GoogleClient(LLMClient):
    """Client for Google Gemini API.
    
    Parameters
    ----------
    api_key : str
        Google API key for authentication.
    model : str, optional
        Model name to use (default: 'gemini-2.0-flash').
    """

    DEFAULT_MODELS = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro",
        "gemini-pro-vision",
    ]

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash") -> None:
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY", "")
        if not self.api_key:
            raise ValueError("Google API Key is required. Set it in settings or GOOGLE_API_KEY environment variable.")
        self.model = model
        genai.configure(api_key=self.api_key)

    @property
    def provider_name(self) -> str:
        return "google"

    @property
    def supported_models(self) -> List[str]:
        return self.DEFAULT_MODELS

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict]:
        """Convert standard message format to Gemini format."""
        converted = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            converted.append({"role": role, "parts": [msg["content"]]})
        return converted

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send a list of messages to the Gemini API.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            The assistant's reply as a string.
        """
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 2048)
        
        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        contents = self._convert_messages(messages)
        
        model_instance = genai.GenerativeModel(model_name=self.model)
        response = model_instance.generate_content(
            contents=contents,
            generation_config=generation_config,
        )
        
        return response.text or ""

    async def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """Send a streaming chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            **kwargs: Additional parameters.
            
        Yields:
            Chunks of the assistant's response as they arrive.
        """
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 2048)
        
        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        contents = self._convert_messages(messages)
        
        model_instance = genai.GenerativeModel(model_name=self.model)
        response = await model_instance.generate_content_async(
            contents=contents,
            generation_config=generation_config,
            stream=True,
        )
        
        async for chunk in response:
            if chunk.text:
                yield chunk.text

    def list_models(self) -> List[str]:
        """Return a list of available models for Google.
        
        Returns:
            List of model identifiers.
        """
        try:
            models = genai.list_models()
            return sorted([m.name.replace("models/", "") for m in models])
        except Exception:
            return self.DEFAULT_MODELS

    def test_connection(self) -> bool:
        """Test the connection to Google API.
        
        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            model_instance = genai.GenerativeModel(model_name=self.model)
            model_instance.generate_content("test")
            return True
        except Exception:
            return False


def get_client(api_key: Optional[str] = None, model: Optional[str] = None) -> GoogleClient:
    """Factory function to get a Google client instance.
    
    Args:
        api_key: Optional API key override.
        model: Optional model override.
        
    Returns:
        Configured GoogleClient instance.
    """
    cfg = Config()
    return GoogleClient(
        api_key=api_key or cfg.get("google_api_key", ""),
        model=model or cfg.get("google_model", "gemini-2.0-flash"),
    )


