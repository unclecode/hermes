from .base import SourceStrategy
from ...utils.audio import download_youtube_audio
from typing import Any
from pydub import AudioSegment

class YouTubeSourceStrategy(SourceStrategy):
    def get_audio(self, source: str) -> bytes:
        audioSegment : AudioSegment = download_youtube_audio(source)
        return audioSegment.export(format="mp3").read()
