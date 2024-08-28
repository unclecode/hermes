# hermes/strategies/source/youtube.py

from .base import SourceStrategy
from ...utils.audio import download_youtube_audio
from typing import Any
from pydub import AudioSegment
import yt_dlp
import tempfile
import os

class YouTubeSourceStrategy(SourceStrategy):
    def get_audio(self, source: str) -> bytes:
        audioSegment : AudioSegment = download_youtube_audio(source)
        return audioSegment.export(format="mp3").read()

    def get_video(self, source: str) -> bytes:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': '%(id)s.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(source, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as video_file:
            video_data = video_file.read()

        os.remove(filename)
        return video_data