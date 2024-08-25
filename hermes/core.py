import os
from typing import Optional, Dict, Any
from .strategies.source import SourceStrategy
from .strategies.provider import ProviderStrategy
from .utils.cache import Cache
from .utils.llm import LLMProcessor
from .config import CONFIG

class Hermes:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or CONFIG
        self.source_strategy = SourceStrategy.get_strategy(self.config['source_type'])
        self.provider_strategy = ProviderStrategy.get_strategy(self.config['transcription']['provider'])
        self.cache = Cache(self.config['cache'])
        self.llm_processor = LLMProcessor()

    def transcribe(self, source: str, force: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Transcribe audio from the given source.
        
        :param source: The source of the audio (file path, URL, etc.)
        :param force: If True, ignore cache and force new transcription
        :param kwargs: Additional arguments for the provider
        :return: A dictionary containing the transcription and metadata
        """
        cache_key = f"{self.source_strategy.__class__.__name__}_{self.provider_strategy.__class__.__name__}_{self.config['transcription']['provider']}_{self.config['transcription']['model']}_{kwargs.get('response_format', 'text')}_{source.replace('/', '_')}"
        
        if not force:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result

        audio_data = self.source_strategy.get_audio(source)
        transcription = self.provider_strategy.transcribe(audio_data, params={**kwargs, **self.config['transcription']})
        
        result = {
            "source": source,
            "provider": self.provider_strategy.__class__.__name__,
            "transcription": transcription
        }
        
        self.cache.set(cache_key, result)
        return result

    def process_with_llm(self, transcription: str, prompt: str) -> str:
        """
        Process the transcription with a language model.

        :param transcription: The transcription text to process
        :param prompt: The prompt to send to the language model
        :return: The processed result from the language model
        """
        return self.llm_processor.process(transcription, prompt)

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'Hermes':
        """
        Create a Hermes instance from a configuration dictionary.
        
        :param config: A dictionary containing configuration options
        :return: A configured Hermes instance
        """
        source_strategy = SourceStrategy.get_strategy(config['source_type'])
        provider_strategy = ProviderStrategy.get_strategy(config['transcription']['provider'])
        
        return cls(config)

def transcribe(source: str, provider: Optional[str] = None, force: bool = False, llm_prompt: Optional[str] = None, model: Optional[str] = None, response_format: str = "text", **kwargs) -> Dict[str, Any]:
    """
    Convenience function to transcribe audio and optionally process with LLM.

    :param source: The source of the audio (file path, URL, etc.)
    :param provider: The name of the provider to use (default: None, will use the default provider)
    :param force: If True, ignore cache and force new transcription
    :param llm_prompt: If provided, process the transcription with this prompt using an LLM
    :param model: The model to use for transcription
    :param response_format: The desired response format (default: "text")
    :param kwargs: Additional arguments for the provider
    :return: A dictionary containing the transcription, metadata, and optional LLM processing result
    """
    config = {
        **CONFIG,
        'source_type': 'auto',
        'transcription': {
            'provider': provider or CONFIG['transcription']['provider'],
            'model': model or CONFIG['transcription']['model'],
        }
    }
    hermes = Hermes.from_config(config)
    result = hermes.transcribe(source, force=force, response_format=response_format, **kwargs)

    if llm_prompt:
        result['llm_processed'] = hermes.process_with_llm(result['transcription'], llm_prompt)

    return result