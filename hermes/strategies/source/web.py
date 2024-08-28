# hermes/strategies/source/web.py

from .base import SourceStrategy
from ...utils.audio import download_web_audio
from typing import Any
import requests

class WebSourceStrategy(SourceStrategy):
    def get_audio(self, source: str) -> bytes:
        audio_data = download_web_audio(source)
        return audio_data.export(format="mp3").read()

    def get_video(self, source: str) -> bytes:
        response = requests.get(source)
        response.raise_for_status()
        return response.content