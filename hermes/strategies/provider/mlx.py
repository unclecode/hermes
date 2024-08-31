import tempfile
import subprocess
import shutil
from typing import Dict, Any
from .base import ProviderStrategy

class MLXProviderStrategy(ProviderStrategy):
    def __init__(self):
        self._check_mlx_whisper_installed()

    def _check_mlx_whisper_installed(self):
        if shutil.which("mlx_whisper") is None:
            raise EnvironmentError(
                "The 'mlx_whisper' command is not found. "
                "Please install it using the following command:\n"
                "pip install mlx-whisper"
            )

    def transcribe(self, audio_data: bytes, params: Dict[str, Any] = None) -> str:
        params = params or {}
        model = params.get("model", "mlx-community/distil-whisper-large-v3")
        output_dir = params.get("output_dir", ".")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_audio.write(audio_data)
            temp_audio_path = temp_audio.name

        command = [
            "mlx_whisper",
            temp_audio_path,
            "--model", model,
            "--output-dir", output_dir,
        ]

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"MLX Whisper transcription failed: {e.stderr}")

        # Assuming the output is in the same directory with the same name as the input file
        output_file = f"{output_dir}/{temp_audio_path.split('/')[-1]}.txt"
        with open(output_file, 'r') as f:
            transcription = f.read()

        return transcription