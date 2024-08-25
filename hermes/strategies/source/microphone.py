from .base import SourceStrategy
from ...utils.audio import record_audio
from typing import Any

class MicrophoneSourceStrategy(SourceStrategy):
    def get_audio(self, source: str) -> bytes:
        audio_data = record_audio()
        return audio_data.export(format="mp3").read()