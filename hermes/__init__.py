from .core import Hermes, transcribe, generate_video_commentary, generate_textual_commentary
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
    "generate_video_commentary",
    "generate_textual_commentary",
    "CONFIG",
    "SourceStrategy",
    "ProviderStrategy",
    "Cache",
    "LLMProcessor",
]
