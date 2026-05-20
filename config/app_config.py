"""Application configuration handling.

This module provides a simple ``Config`` class that loads and saves
configuration values to a JSON file located at ``config/config.json``.
The configuration is used to store user‑provided settings such as the
OpenAI API key, the selected model provider and the model name.  The
class offers ``get`` and ``set`` methods for convenient access and
automatically persists changes to disk.

The file is deliberately lightweight and has no external dependencies
apart from the Python standard library, making it safe to import from
any part of the application (including the UI code).
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict


class Config:
    """Singleton‑style configuration manager.

    The configuration is stored as a JSON dictionary.  If the file does
    not exist, a default configuration is created.  All changes are
    written back to the file immediately to keep the on‑disk state in
    sync with the in‑memory representation.
    """

    _instance: "Config | None" = None
    _config_path: str = "config/config.json"

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self) -> None:
        """Load configuration from the configuration file.

        If the file is missing or malformed, a fresh default configuration
        is written to disk.
        """
        default: Dict[str, Any] = {
            "api_key": os.environ.get("OPENAI_API_KEY", ""),
            "model_provider": "openai",
            "model_name": "gpt-4o-mini",
            "ollama_url": "http://localhost:11434",
        }
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                # Corrupted file – reset to defaults
                self._data = default
                self._save()
        else:
            self._data = default
            self._save()

    def _save(self) -> None:
        """Persist the current configuration to ``config.json``."""
        os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=4, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value.

        ``default`` is returned when the key is not present.
        """
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and immediately persist it."""
        self._data[key] = value
        self._save()

    def as_dict(self) -> Dict[str, Any]:
        """Return a shallow copy of the configuration dictionary."""
        return dict(self._data)
