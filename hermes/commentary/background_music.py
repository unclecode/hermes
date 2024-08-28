from moviepy.editor import AudioFileClip, CompositeAudioClip

class BackgroundMusic:
    def __init__(self, audio_path, volume=0.2, fade_duration=3):
        self.audio = AudioFileClip(audio_path)
        self.volume = volume
        self.fade_duration = fade_duration

    def prepare_for_video(self, video_duration):
        music = self.audio.audio_fadein(self.fade_duration)
        if self.audio.duration < video_duration:
            loops_needed = int(video_duration / self.audio.duration) + 1
            music = CompositeAudioClip([music] * loops_needed)
        music = music.subclip(0, video_duration).audio_fadeout(self.fade_duration)
        return music.volumex(self.volume)