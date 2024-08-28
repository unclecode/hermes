from .core import Hermes, transcribe
from .config import CONFIG
from .strategies.source import SourceStrategy
from .strategies.provider import ProviderStrategy
from .utils.cache import Cache
from .utils.llm import LLMProcessor
from .cli import main as cli_main

__version__ = "0.2.0"

__all__ = [
    "Hermes",
    "transcribe",
    "CONFIG",
    "SourceStrategy",
    "ProviderStrategy",
    "Cache",
    "LLMProcessor",
]
