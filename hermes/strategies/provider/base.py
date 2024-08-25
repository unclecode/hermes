from abc import ABC, abstractmethod
from typing import Dict, Any

class ProviderStrategy(ABC):
    @abstractmethod
    def transcribe(self, audio_data: bytes, params: Dict[str, Any] = None) -> str:
        pass

    @classmethod
    def get_strategy(cls, provider_type: str) -> 'ProviderStrategy':
        if provider_type == 'groq':
            from .groq import GroqProviderStrategy
            return GroqProviderStrategy()
        elif provider_type == 'openai':
            from .openai import OpenAIProviderStrategy
            return OpenAIProviderStrategy()
        elif provider_type == 'mlx':
            from .mlx import MLXProviderStrategy
            return MLXProviderStrategy()
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")