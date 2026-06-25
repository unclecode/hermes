import os
import tempfile
from urllib.parse import urlparse
from typing import Dict, Any
from .base import ProviderStrategy


class TwelveLabsProviderStrategy(ProviderStrategy):
    """Transcribe via TwelveLabs Pegasus, a video-understanding model.

    Unlike the Whisper-based providers, Pegasus reasons over the *video* itself
    rather than an extracted audio track, so it can use on-screen text and
    visual context to improve the transcript. It accepts the original source
    directly: a public URL is passed through as-is, while a local file is
    uploaded as a TwelveLabs asset before analysis.
    """

    DEFAULT_MODEL = "pegasus1.5"
    DEFAULT_PROMPT = (
        "Transcribe all spoken words in this video verbatim. "
        "Output only the transcript text, with no commentary, labels, or "
        "timestamps. If there is no speech, output an empty string."
    )
    # Pegasus requires max_tokens >= 512 (analyze, non-segmented mode).
    DEFAULT_MAX_TOKENS = 4096

    def __init__(self):
        self.api_key = os.getenv("TWELVELABS_API_KEY")
        if not self.api_key:
            raise ValueError("TWELVELABS_API_KEY environment variable is not set")
        try:
            from twelvelabs import TwelveLabs
        except ImportError as e:
            raise ImportError(
                "The 'twelvelabs' package is required for the TwelveLabs provider. "
                "Install it with: pip install hermes[twelvelabs]"
            ) from e
        self.client = TwelveLabs(api_key=self.api_key)

    def transcribe(self, audio_data: bytes, params: Dict[str, Any] = None) -> str:
        from twelvelabs.types.video_context import (
            VideoContext_Url,
            VideoContext_AssetId,
        )

        params = params or {}
        model = params.get("model") or self.DEFAULT_MODEL
        prompt = params.get("prompt") or self.DEFAULT_PROMPT
        max_tokens = params.get("max_tokens", self.DEFAULT_MAX_TOKENS)
        source = params.get("source")

        if self._is_public_url(source):
            video = VideoContext_Url(url=source)
        else:
            video = VideoContext_AssetId(asset_id=self._upload(source, audio_data))

        response = self.client.analyze(
            model_name=model,
            video=video,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=params.get("temperature", 0),
        )
        return response.data

    def _upload(self, source: str, audio_data: bytes) -> str:
        """Upload the original video (preferred) or the audio fallback as an asset."""
        if source and os.path.isfile(source):
            with open(source, "rb") as f:
                asset = self.client.assets.create(
                    method="direct",
                    file=(os.path.basename(source), f.read()),
                )
        else:
            # No usable local file (e.g. YouTube/mic source): fall back to the
            # audio bytes Hermes already extracted, wrapped in a container.
            with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
                tmp.write(audio_data)
                tmp.flush()
                tmp.seek(0)
                asset = self.client.assets.create(
                    method="direct",
                    file=("audio.wav", tmp.read(), "audio/wav"),
                )
        return asset.id

    @staticmethod
    def _is_public_url(source: str) -> bool:
        if not source:
            return False
        parsed = urlparse(source)
        if parsed.scheme not in ("http", "https"):
            return False
        # TwelveLabs cannot fetch YouTube watch pages directly; those are
        # uploaded as assets from the audio Hermes already downloaded.
        return parsed.netloc not in ("www.youtube.com", "youtube.com", "youtu.be")
