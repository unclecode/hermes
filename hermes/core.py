import os
from typing import Optional, Dict, Any
from .strategies.source import SourceStrategy
from .strategies.provider import ProviderStrategy
from .utils.cache import Cache
from .utils.llm import LLMProcessor
from .config import CONFIG
from .commentary.video_commentary import VideoCommentary
from .commentary.background_music import BackgroundMusic
from .commentary.tts import TTSSettings
import tempfile
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
    
    def generate_video_commentary(self, source: str, force: bool = False, bg_music_path: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        cache_key = f"video_commentary_{self.source_strategy.__class__.__name__}_{source.replace('/', '_')}"

        if not force:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result

        video_data = self.source_strategy.get_video(source)
        
        commentary = VideoCommentary(base_folder=self.config['cache']['directory'])
        
        bg_music = None
        if bg_music_path:
            bg_music = BackgroundMusic(bg_music_path,
                                    volume=self.config['background_music']['volume'],
                                    fade_duration=self.config['background_music']['fade_duration'])
        
        tts_settings = TTSSettings(provider=self.config['tts']['provider'],
                                voice_id=self.config['tts']['voice_id'])

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
            temp_video_file.write(video_data)
            temp_video_path = temp_video_file.name

        result = commentary.generate_audio_commentary(
            video_path=temp_video_path,
            background_music=bg_music,
            tts_settings=tts_settings,
            **kwargs
        )

        os.unlink(temp_video_path)  # Remove the temporary video file

        final_result = {
            "commentary": commentary.get_comments(),
            "final_video_path": str(commentary.get_final_video_path())
        }

        self.cache.set(cache_key, final_result)
        return final_result

    def generate_textual_commentary(self, 
                                    source: str, 
                                    video_topic: str = 'general',
                                    commentary_type: str = 'detailed',
                                    transcription : str = None,
                                    force: bool = False, 
                                    llm_prompt: Optional[str] = None, 
                                    **kwargs) -> Dict[str, Any]:
        cache_key = f"textual_commentary_{self.source_strategy.__class__.__name__}_{source.replace('/', '_')}"

        if not force:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result

        video_data = self.source_strategy.get_video(source)  # Now using get_video instead of get_audio
        
        commentary = VideoCommentary(base_folder=self.config['cache']['directory'])

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
            temp_video_file.write(video_data)
            temp_video_path = temp_video_file.name

        textual_commentary = commentary.generate_textual_commentary(
            video_path=temp_video_path,
            video_topic=video_topic,
            commentary_type=commentary_type,
            transcription = transcription,
            **kwargs)

        os.unlink(temp_video_path)  # Remove the temporary video file

        result = {"textual_commentary": textual_commentary}

        if llm_prompt:
            result["llm_processed"] = self.process_with_llm(textual_commentary, llm_prompt)

        self.cache.set(cache_key, result)
        return result


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

def generate_video_commentary(source: str, force: bool = False, bg_music_path: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to generate video commentary.

    :param source: The source of the video (file path, URL, etc.)
    :param force: If True, ignore cache and force new commentary generation
    :param bg_music_path: The path to the background music file
    :param kwargs: Additional arguments for the commentary generation
    :return: A dictionary containing the commentary and the path to the final video
    """
    config = {
        **CONFIG,
        'source_type': 'auto',
    }
    hermes = Hermes.from_config(config)
    return hermes.generate_video_commentary(source, force=force, bg_music_path=bg_music_path, **kwargs)


def generate_textual_commentary(source: str, transcription : str = None, force: bool = False, llm_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to generate textual commentary.

    :param source: The source of the video (file path, URL, etc.)
    :param transcription: The transcription of the video
    :param force: If True, ignore cache and force new commentary generation
    :param llm_prompt: If provided, process the textual commentary with this prompt using an LLM
    :param kwargs: Additional arguments for the commentary generation
    :return: A dictionary containing the textual commentary and optional LLM processing result
    """
    config = {
        **CONFIG,
        'source_type': 'auto',
    }
    hermes = Hermes.from_config(config)
    
    return hermes.generate_textual_commentary(source, transcription = transcription, force=force, llm_prompt=llm_prompt, **kwargs)