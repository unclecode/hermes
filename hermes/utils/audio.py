import os
import tempfile
from typing import Any
import yt_dlp
import pyperclip
import sounddevice as sd
import numpy as np
import requests
from pydub import AudioSegment

def load_audio_file(file_path: str) -> AudioSegment:
    """
    Load an audio file using pydub.

    :param file_path: Path to the audio file
    :return: AudioSegment object
    """
    return AudioSegment.from_file(file_path)

def download_youtube_audio(url: str) -> AudioSegment:
    """
    Download audio from a YouTube video.

    :param url: YouTube video URL
    :return: AudioSegment object
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(id)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = f"{info['id']}.mp3"

    audio = AudioSegment.from_mp3(filename)
    os.remove(filename)
    return audio

def record_audio(duration: int = 10, sample_rate: int = 44100) -> AudioSegment:
    """
    Record audio from the microphone.

    :param duration: Recording duration in seconds
    :param sample_rate: Sample rate for recording
    :return: AudioSegment object
    """
    print(f"Recording for {duration} seconds...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2)
    sd.wait()
    print("Recording finished.")

    # Convert numpy array to AudioSegment
    audio = AudioSegment(
        recording.tobytes(),
        frame_rate=sample_rate,
        sample_width=recording.dtype.itemsize,
        channels=2
    )
    return audio

def get_audio_from_clipboard() -> AudioSegment:
    """
    Get audio data from the clipboard.

    :return: AudioSegment object
    """
    clipboard_content = pyperclip.paste()
    if clipboard_content.startswith(('http://', 'https://')):
        return download_web_audio(clipboard_content)
    else:
        raise ValueError("No valid audio URL found in clipboard")

def download_web_audio(url: str) -> AudioSegment:
    """
    Download audio from a web URL.

    :param url: URL of the audio file
    :return: AudioSegment object
    """
    response = requests.get(url)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
        temp_file.write(response.content)
        temp_file_path = temp_file.name

    audio = AudioSegment.from_mp3(temp_file_path)
    os.remove(temp_file_path)
    return audio

def convert_to_wav(audio: AudioSegment, sample_rate: int = 16000) -> bytes:
    """
    Convert AudioSegment to WAV format with specified sample rate.

    :param audio: AudioSegment object
    :param sample_rate: Desired sample rate
    :return: WAV audio data as bytes
    """
    try:
        audio = audio.set_frame_rate(sample_rate).set_channels(1)
        buffer = audio.export(format="wav")
        return buffer.read()
    except Exception as e:
        print(f"Error converting audio to WAV: {e}")
        return None

def get_audio_duration(audio: AudioSegment) -> float:
    """
    Get the duration of an AudioSegment in seconds.

    :param audio: AudioSegment object
    :return: Duration in seconds
    """
    return len(audio) / 1000.0
