import tempfile
import subprocess
from typing import Dict, Any
from .base import ProviderStrategy

class MLXProviderStrategy(ProviderStrategy):
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

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"MLX Whisper transcription failed: {result.stderr}")

        # Assuming the output is in the same directory with the same name as the input file
        output_file = f"{output_dir}/{temp_audio_path.split('/')[-1]}.txt"
        with open(output_file, 'r') as f:
            transcription = f.read()

        return transcription
