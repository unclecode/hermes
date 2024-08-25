from .base import SourceStrategy
from ...utils.audio import download_web_audio
from typing import Any
class WebSourceStrategy(SourceStrategy):
    def get_audio(self, source: str) -> bytes:
        audio_data = download_web_audio(source)
        return audio_data.export(format="mp3").read()