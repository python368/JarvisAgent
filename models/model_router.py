"""Model router to select appropriate AI client based on configuration.

The router reads the ``model_provider`` setting from :class:`config.app_config.Config`
and returns an instance of either :class:`models.openai_client.OpenAIClient`
or :class:`models.ollama_client.OllamaClient`.
"""

from __future__ import annotations

from config.app_config import Config

# Import clients lazily to avoid unnecessary dependencies if not used.
try:
    from models.openai_client import OpenAIClient
except Exception:  # pragma: no cover
    OpenAIClient = None

try:
    from models.ollama_client import OllamaClient
except Exception:  # pragma: no cover
    OllamaClient = None


def get_client() -> object:
    """Return an AI client instance based on the current configuration.

    The function reads ``model_provider``, ``api_key``, ``model_name`` and
    ``ollama_url`` from the configuration.  If the provider is ``OpenAI`` an
    :class:`OpenAIClient` is instantiated; if ``Ollama`` an :class:`OllamaClient`
    is instantiated.  Unsupported providers raise ``ValueError``.
    """
    cfg = Config()
    provider = cfg.get("model_provider")
    api_key = cfg.get("api_key")
    model_name = cfg.get("model_name")
    if provider == "openai":
        if OpenAIClient is None:
            raise ImportError("OpenAIClient could not be imported")
        return OpenAIClient(api_key=api_key, model=model_name)
    if provider == "ollama":
        if OllamaClient is None:
            raise ImportError("OllamaClient could not be imported")
        ollama_url = cfg.get("ollama_url")
        return OllamaClient(base_url=ollama_url, model=model_name)
    raise ValueError(f"Unsupported model provider: {provider}")
