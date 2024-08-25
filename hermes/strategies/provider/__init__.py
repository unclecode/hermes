from .base import ProviderStrategy

def get_provider_strategy(provider_name: str) -> ProviderStrategy:
    if provider_name == 'groq':
        from .groq import GroqProviderStrategy
        return GroqProviderStrategy()
    elif provider_name == 'openai':
        from .openai import OpenAIProviderStrategy
        return OpenAIProviderStrategy()
    elif provider_name == 'mlx':
        from .mlx import MLXProviderStrategy
        return MLXProviderStrategy()
    else:
        raise ValueError(f"Unknown provider: {provider_name}")