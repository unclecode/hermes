import os
import sys
import types
from unittest.mock import MagicMock, patch

import pytest


def _install_fake_twelvelabs(monkeypatch):
    """Stub the optional `twelvelabs` SDK so the provider imports without it."""
    tl = types.ModuleType("twelvelabs")
    tl.TwelveLabs = MagicMock(name="TwelveLabs")

    vc = types.ModuleType("twelvelabs.types.video_context")
    vc.VideoContext_Url = lambda url: ("url", url)
    vc.VideoContext_AssetId = lambda asset_id: ("asset", asset_id)

    types_mod = types.ModuleType("twelvelabs.types")
    monkeypatch.setitem(sys.modules, "twelvelabs", tl)
    monkeypatch.setitem(sys.modules, "twelvelabs.types", types_mod)
    monkeypatch.setitem(sys.modules, "twelvelabs.types.video_context", vc)
    return tl


def _load_provider(monkeypatch):
    """Import the provider module directly, bypassing hermes package __init__.

    The real package __init__ pulls in heavy media deps (ffmpeg, sounddevice,
    ...). We load the provider under a throwaway package whose only member is a
    stub `base` that satisfies the module's relative import.
    """
    import importlib.util

    _install_fake_twelvelabs(monkeypatch)
    monkeypatch.setenv("TWELVELABS_API_KEY", "fake_key")

    pkg = types.ModuleType("_tl_test_pkg")
    pkg.__path__ = []  # mark as package
    base = types.ModuleType("_tl_test_pkg.base")

    class ProviderStrategy:  # minimal stand-in for the ABC
        pass

    base.ProviderStrategy = ProviderStrategy
    monkeypatch.setitem(sys.modules, "_tl_test_pkg", pkg)
    monkeypatch.setitem(sys.modules, "_tl_test_pkg.base", base)

    path = os.path.join(
        os.path.dirname(__file__), "..", "hermes", "strategies", "provider", "twelvelabs.py"
    )
    spec = importlib.util.spec_from_file_location(
        "_tl_test_pkg.twelvelabs", os.path.abspath(path)
    )
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "_tl_test_pkg.twelvelabs", module)
    spec.loader.exec_module(module)
    return module


def test_requires_api_key(monkeypatch):
    module = _load_provider(monkeypatch)
    monkeypatch.delenv("TWELVELABS_API_KEY", raising=False)
    with pytest.raises(ValueError):
        module.TwelveLabsProviderStrategy()


def test_public_url_uses_url_context(monkeypatch):
    module = _load_provider(monkeypatch)
    strategy = module.TwelveLabsProviderStrategy()
    strategy.client.analyze.return_value = MagicMock(data="hello world")

    result = strategy.transcribe(
        b"", {"source": "https://example.com/video.mp4", "model": "pegasus1.5"}
    )

    assert result == "hello world"
    kwargs = strategy.client.analyze.call_args.kwargs
    assert kwargs["video"] == ("url", "https://example.com/video.mp4")
    assert kwargs["model_name"] == "pegasus1.5"
    assert kwargs["max_tokens"] >= 512  # Pegasus floor
    strategy.client.assets.create.assert_not_called()


def test_youtube_url_is_uploaded_not_passed_through(monkeypatch):
    module = _load_provider(monkeypatch)
    strategy = module.TwelveLabsProviderStrategy()
    strategy.client.assets.create.return_value = MagicMock(id="asset123")
    strategy.client.analyze.return_value = MagicMock(data="yt transcript")

    result = strategy.transcribe(
        b"audio-bytes", {"source": "https://www.youtube.com/watch?v=abc"}
    )

    assert result == "yt transcript"
    strategy.client.assets.create.assert_called_once()
    assert strategy.client.analyze.call_args.kwargs["video"] == ("asset", "asset123")


def test_local_file_is_uploaded_as_asset(monkeypatch, tmp_path):
    module = _load_provider(monkeypatch)
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"\x00\x01video")

    strategy = module.TwelveLabsProviderStrategy()
    strategy.client.assets.create.return_value = MagicMock(id="local999")
    strategy.client.analyze.return_value = MagicMock(data="local transcript")

    result = strategy.transcribe(b"wav", {"source": str(video)})

    assert result == "local transcript"
    strategy.client.assets.create.assert_called_once()
    assert strategy.client.analyze.call_args.kwargs["video"] == ("asset", "local999")


@pytest.mark.skipif(
    not os.getenv("TWELVELABS_API_KEY"),
    reason="TWELVELABS_API_KEY not set; skipping live TwelveLabs API test",
)
def test_live_pegasus_wiring(tmp_path):
    """End-to-end: upload a short generated clip and run Pegasus analyze.

    Asserts the request wiring works and returns a string. The clip has no
    speech, so the transcript is expected to be empty/whitespace.
    """
    import subprocess

    clip = tmp_path / "live.mp4"
    proc = subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "testsrc=duration=5:size=640x360:rate=15",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=5",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
            str(clip),
        ],
        capture_output=True,
    )
    if proc.returncode != 0:
        pytest.skip("ffmpeg unavailable; cannot build live test clip")

    # Import the real module path so the actual SDK is used.
    from hermes.strategies.provider.twelvelabs import TwelveLabsProviderStrategy

    strategy = TwelveLabsProviderStrategy()
    result = strategy.transcribe(b"", {"source": str(clip), "max_tokens": 512})
    assert isinstance(result, str)
