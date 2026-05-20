"""Simple Ollama client.

Provides a thin wrapper around the Ollama HTTP API for chat completions.
The implementation uses the ``requests`` library (already a project
dependency) and mirrors the interface of :class:`models.openai_client.OpenAIClient`
so that :func:`models.model_router.get_client` can treat both clients
interchangeably.
"""

from __future__ import annotations

import json
from typing import List, Dict, Any

import requests


class OllamaClient:
    """Client for Ollama's ``/api/chat`` endpoint.

    Parameters
    ----------
    base_url: str, optional
        Base URL of the Ollama server (default ``http://localhost:11434``).
    model: str, optional
        Model name to use for chat completions (default ``"llama2"``).
    """

    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send a list of messages to Ollama and return the assistant reply.

        The ``messages`` argument follows the same schema as the OpenAI API –
        each entry is a ``{"role": "user"|"assistant"|"system", "content": str}``.
        Ollama expects a JSON payload with ``model`` and ``messages`` keys.
        The method performs a blocking request and returns the ``content``
        field of the ``message`` object from the response.
        """
        payload = {"model": self.model, "messages": messages}
        try:
            resp = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=30)
            resp.raise_for_status()
        except Exception as exc:
            raise RuntimeError(f"Ollama request failed: {exc}")
        data = resp.json()
        # Ollama returns a ``message`` dict with ``content``.
        return data.get("message", {}).get("content", "")

    def list_models(self) -> List[str]:
        """Return a list of model names available on the Ollama server.

        The endpoint ``/api/tags`` returns a JSON object with a ``models``
        list; each entry contains a ``name`` field.
        """
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=30)
            resp.raise_for_status()
        except Exception as exc:
            raise RuntimeError(f"Failed to list Ollama models: {exc}")
        data = resp.json()
        return [model.get("name", "") for model in data.get("models", [])]
