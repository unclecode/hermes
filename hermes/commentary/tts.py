import os
import requests
import tempfile
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

class TTSSettings:
    def __init__(self, provider='openai', voice_id='alloy', stability=0.0, similarity_boost=1.0, style=0.0, use_speaker_boost=True):
        self.provider = provider
        self.voice_id = voice_id
        self.stability = stability
        self.similarity_boost = similarity_boost
        self.style = style
        self.use_speaker_boost = use_speaker_boost

class TextToSpeech:
    def __init__(self, settings: TTSSettings):
        self.settings = settings
        self.openai_client = None
        self.elevenlabs_client = None

        if self.settings.provider == 'openai':
            self.openai_client = requests.Session()
        elif self.settings.provider == 'elevenlabs':
            self.elevenlabs_client = ElevenLabs(api_key=os.environ.get("ELEVENLABS_API_KEY"))

    def generate_audio(self, text):
        if self.settings.provider == 'openai':
            return self._generate_audio_openai(text)
        elif self.settings.provider == 'elevenlabs':
            return self._generate_audio_elevenlabs(text)
        else:
            raise ValueError("Unsupported TTS provider")

    def _generate_audio_openai(self, text):
        response = self.openai_client.post(
            "https://api.openai.com/v1/audio/speech",
            headers={"Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}"},
            json={"model": "tts-1", "input": text, "voice": self.settings.voice_id},
        )
        return response.content

    def _generate_audio_elevenlabs(self, text):
        response = self.elevenlabs_client.text_to_speech.convert(
            voice_id=self.settings.voice_id,
            output_format="mp3_22050_32",
            text=text,
            model_id="eleven_turbo_v2_5",
            voice_settings=VoiceSettings(
                stability=self.settings.stability,
                similarity_boost=self.settings.similarity_boost,
                style=self.settings.style,
                use_speaker_boost=self.settings.use_speaker_boost,
            ),
        )
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        for chunk in response:
            if chunk:
                temp_file.write(chunk)
        temp_file.close()
        
        return temp_file.name