from urllib.parse import urlparse
from .base import SourceStrategy
from .file import FileSourceStrategy
from .youtube import YouTubeSourceStrategy
from .web import WebSourceStrategy

class AutoSourceStrategy(SourceStrategy):
    def get_audio(self, source: str) -> bytes:
        if self.is_youtube_url(source):
            return YouTubeSourceStrategy().get_audio(source)
        elif self.is_web_url(source):
            return WebSourceStrategy().get_audio(source)
        else:
            return FileSourceStrategy().get_audio(source)

    @staticmethod
    def is_youtube_url(url: str) -> bool:
        parsed = urlparse(url)
        return parsed.netloc in ['www.youtube.com', 'youtube.com', 'youtu.be']

    @staticmethod
    def is_web_url(url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in ['http', 'https']