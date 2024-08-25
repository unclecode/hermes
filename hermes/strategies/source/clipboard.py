from .base import SourceStrategy
from ...utils.audio import get_audio_from_clipboard
from typing import Any
class ClipboardSourceStrategy(SourceStrategy):
    def get_audio(self, source: str) -> bytes:
        audio_data = get_audio_from_clipboard()
        return audio_data.export(format="mp3").read()
