# hermes/strategies/source/file.py

import os
from .base import SourceStrategy
from ...utils.audio import load_audio_file, convert_to_wav
from typing import Any

class FileSourceStrategy(SourceStrategy):
    def get_audio(self, source: str) -> bytes:
        abs_path = os.path.abspath(source)
        if not os.path.isfile(abs_path):
            raise FileNotFoundError(f"The file {abs_path} does not exist")
        audio = load_audio_file(abs_path)
        return convert_to_wav(audio)

    def get_video(self, source: str) -> bytes:
        abs_path = os.path.abspath(source)
        if not os.path.isfile(abs_path):
            raise FileNotFoundError(f"The file {abs_path} does not exist")
        with open(abs_path, 'rb') as video_file:
            return video_file.read()