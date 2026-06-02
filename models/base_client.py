"""Base interface for LLM clients.

This module defines the abstract base class that all LLM provider clients
must implement. This ensures a consistent interface across different providers
(OpenAI, Anthropic, Google, Ollama, etc.).
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Dict, Any, Optional


class LLMClient(ABC):
    """Abstract base class for LLM provider clients.
    
    All provider clients must implement these methods to ensure
    interchangeability across the application.
    """
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send a chat completion request and return the response.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional provider-specific parameters.
            
        Returns:
            The assistant's response as a string.
        """
        pass
    
    @abstractmethod
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """Send a streaming chat completion request.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional provider-specific parameters.
            
        Yields:
            Chunks of the assistant's response as they arrive.
        """
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """Return a list of available models from this provider.
        
        Returns:
            List of model identifiers.
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test the connection to the provider.
        
        Returns:
            True if the connection is successful, False otherwise.
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name (e.g., 'openai', 'anthropic', 'ollama')."""
        pass
    
    @property
    @abstractmethod
    def supported_models(self) -> List[str]:
        """Return a list of commonly used models for this provider."""
        pass