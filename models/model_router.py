"""Model router to select appropriate AI client based on configuration.

The router reads the provider setting from Config and returns an instance
of the appropriate LLM client. All clients implement the LLMClient interface
for seamless interchangeability.
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from config.app_config import Config

if TYPE_CHECKING:
    from models.base_client import LLMClient


# Lazy imports to avoid unnecessary dependencies if not used
_OPENAI_CLIENT = None
_ANTHROPIC_CLIENT = None
_OLLAMA_CLIENT = None
_GOOGLE_CLIENT = None


def _get_openai_client():
    global _OPENAI_CLIENT
    if _OPENAI_CLIENT is None:
        from models.openai_client import OpenAIClient
        _OPENAI_CLIENT = OpenAIClient
    return _OPENAI_CLIENT


def _get_anthropic_client():
    global _ANTHROPIC_CLIENT
    if _ANTHROPIC_CLIENT is None:
        from models.anthropic_client import AnthropicClient
        _ANTHROPIC_CLIENT = AnthropicClient
    return _ANTHROPIC_CLIENT


def _get_ollama_client():
    global _OLLAMA_CLIENT
    if _OLLAMA_CLIENT is None:
        from models.ollama_client import OllamaClient
        _OLLAMA_CLIENT = OllamaClient
    return _OLLAMA_CLIENT


def _get_google_client():
    global _GOOGLE_CLIENT
    if _GOOGLE_CLIENT is None:
        from models.google_client import GoogleClient
        _GOOGLE_CLIENT = GoogleClient
    return _GOOGLE_CLIENT


def get_client() -> "LLMClient":
    """Return an LLM client instance based on the current configuration.
    
    Reads provider, API key, model, and provider-specific settings from Config
    and instantiates the appropriate client.
    
    Returns:
        An LLMClient instance for the selected provider.
        
    Raises:
        ValueError: If the provider is not supported or not configured.
    """
    cfg = Config()
    provider = cfg.get("model_provider", "").lower()
    api_key = cfg.get("api_key", "")
    
    if provider in ("openai", "OpenAI"):
        OpenAIClient = _get_openai_client()
        return OpenAIClient(
            api_key=api_key,
            model=cfg.get("model_name", "gpt-4o-mini"),
        )
    
    if provider in ("anthropic", "claude", "Anthropic"):
        AnthropicClient = _get_anthropic_client()
        return AnthropicClient(
            api_key=cfg.get("anthropic_api_key", api_key),
            model=cfg.get("anthropic_model", "claude-3-5-sonnet-20241022"),
        )
    
    if provider in ("ollama", "Ollama"):
        OllamaClient = _get_ollama_client()
        return OllamaClient(
            base_url=cfg.get("ollama_url", "http://localhost:11434"),
            model=cfg.get("ollama_model", "llama3.2"),
        )
    
    if provider in ("google", "gemini", "Google"):
        GoogleClient = _get_google_client()
        return GoogleClient(
            api_key=cfg.get("google_api_key", api_key),
            model=cfg.get("google_model", "gemini-2.0-flash"),
        )
    
    # Default to OpenAI if provider is not recognized
    OpenAIClient = _get_openai_client()
    return OpenAIClient(
        api_key=api_key,
        model=cfg.get("model_name", "gpt-4o-mini"),
    )


def get_available_providers() -> list[str]:
    """Return a list of available/supported providers.
    
    Returns:
        List of provider names.
    """
    return ["OpenAI", "Anthropic", "Ollama", "Google"]


def get_provider_info(provider: str) -> dict:
    """Return information about a specific provider.
    
    Args:
        provider: Provider name (case-insensitive).
        
    Returns:
        Dictionary with provider information.
    """
    info = {
        "openai": {
            "name": "OpenAI",
            "description": "GPT-4o, GPT-4o-mini, GPT-4 and more",
            "requires_api_key": True,
            "default_model": "gpt-4o-mini",
            "supports_streaming": True,
            "supports_vision": True,
        },
        "anthropic": {
            "name": "Anthropic Claude",
            "description": "Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku",
            "requires_api_key": True,
            "default_model": "claude-3-5-sonnet-20241022",
            "supports_streaming": True,
            "supports_vision": True,
        },
        "ollama": {
            "name": "Ollama (Local)",
            "description": "Run open-source models locally",
            "requires_api_key": False,
            "default_model": "llama3.2",
            "supports_streaming": True,
            "supports_vision": False,
        },
        "google": {
            "name": "Google Gemini",
            "description": "Gemini 2.0 Flash, Gemini 1.5 Pro, Gemini 1.5 Flash",
            "requires_api_key": True,
            "default_model": "gemini-2.0-flash",
            "supports_streaming": True,
            "supports_vision": True,
        },
    }
    return info.get(provider.lower(), {})
