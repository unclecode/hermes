# hermes/strategies/source/base.py

from abc import ABC, abstractmethod
from typing import Any

class SourceStrategy(ABC):
    @abstractmethod
    def get_audio(self, source: str) -> bytes:
        """
        Retrieve audio data from the given source.

        :param source: The source identifier (e.g., file path, URL)
        :return: Audio data as bytes in MP3 format
        """
        pass

    @abstractmethod
    def get_video(self, source: str) -> bytes:
        """
        Retrieve video data from the given source.

        :param source: The source identifier (e.g., file path, URL)
        :return: Video data as bytes in MP4 format
        """
        pass

    @classmethod
    def get_strategy(cls, source_type: str) -> 'SourceStrategy':
        """
        Factory method to get the appropriate source strategy.

        :param source_type: The type of source strategy to use
        :return: An instance of the appropriate SourceStrategy subclass
        """
        if source_type == 'auto':
            from .auto import AutoSourceStrategy
            return AutoSourceStrategy()
        elif source_type == 'file':
            from .file import FileSourceStrategy
            return FileSourceStrategy()
        elif source_type == 'youtube':
            from .youtube import YouTubeSourceStrategy
            return YouTubeSourceStrategy()
        elif source_type == 'microphone':
            from .microphone import MicrophoneSourceStrategy
            return MicrophoneSourceStrategy()
        elif source_type == 'clipboard':
            from .clipboard import ClipboardSourceStrategy
            return ClipboardSourceStrategy()
        elif source_type == 'web':
            from .web import WebSourceStrategy
            return WebSourceStrategy()
        else:
            raise ValueError(f"Unknown source type: {source_type}")