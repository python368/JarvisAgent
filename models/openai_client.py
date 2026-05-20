# models/openai_client.py
"""Simple wrapper around the OpenAI API.

This module provides a thin abstraction for making chat completions using the
`openai` Python package.  The implementation is deliberately lightweight – it
loads the API key from the project's configuration (see ``config/app_config``)
and exposes two convenience methods:

* ``chat`` – perform a chat completion given a list of messages.
* ``list_models`` – return a list of model identifiers that the OpenAI service
  reports as available.

The wrapper is used by the UI layer (e.g. ``app/chat_widget.py``) to obtain AI
responses.  Keeping the logic in a separate module makes it easy to replace the
backend (e.g. with Ollama) without touching the UI code.
"""

from __future__ import annotations

import os
from typing import List, Dict, Any

import openai

# Import the Config class we added earlier.  Importing lazily avoids circular
# imports if the config module itself imports any model code.
try:
    from config.app_config import Config
except Exception:  # pragma: no cover – fallback for safety during early import
    Config = None


class OpenAIClient:
    """A minimal client for OpenAI chat completions.

    The client reads the API key from ``Config`` (or the ``OPENAI_API_KEY``
    environment variable) and provides a simple ``chat`` method that returns the
    assistant's reply as a string.
    """

    def __init__(self, api_key: str, model: str) -> None:
        # API key and model are now guaranteed to be provided by model_router.
        self.api_key = api_key
        self.model = model
        openai.api_key = self.api_key

    def chat(self, messages: List[Dict[str, str]], model: str | None = None) -> str:
        """Send a list of messages to the OpenAI chat endpoint."""

        # parameters:
        #     A list of dictionaries with ``role`` ("system", "user", "assistant")
        #     and ``content`` keys, following the OpenAI chat

        #     completion format.
        # model:
        #     The model to use for the chat completion. If not provided, the
        #     client's default model will be used.
        response = openai.chat.completions.create(
            model=model or self.model, messages=messages, temperature=0
        )
        return response.choices[0].message.content or ""

    def list_models(self) -> List[str]:
        """Return a list of available models for the given provider."""

        return sorted([m.id for m in openai.models.list().data])


_client: OpenAIClient | None = None


def get_client(api_key: str | None = None, model: str | None = None) -> OpenAIClient:
    """Return a cached OpenAI client instance."""

    # If parameters are given, always create a fresh client.  This is useful
    # when the user changes their settings via the UI.
    if api_key or model:
        return OpenAIClient(api_key, model)

    # Otherwise, return the cached instance (or create it with defaults).
    global _client
    if _client is None:
        cfg = Config()
        _client = OpenAIClient(cfg.get("api_key"), cfg.get("model_name"))
    return _client