from pathlib import Path
import pickle
import json
from ..utils.commentary import (
    extract_frames, generate_timed_commentary, generate_untimed_commentary,
    create_audio_segments, combine_audio_with_video, save_commentary, extract_frames_fast
)
from .tts import TextToSpeech, TTSSettings
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler and set level to INFO
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# Create formatter
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(levelname)s - %(message)s')
# Add formatter to ch
ch.setFormatter(formatter)
# Add ch to logger
logger.addHandler(ch)

class VideoCommentary:
    def __init__(self, base_folder='commentaries'):
        self.base_folder = Path(base_folder)
        self.video_name = None
        self.comments = []
        self.audio_segments = []
        self.final_video_path = None

    def set_video(self, video_path):
        self.video_name = Path(video_path).stem
        self.project_folder = self.base_folder / self.video_name
        self.project_folder.mkdir(parents=True, exist_ok=True)


    def generate_audio_commentary(self, 
               video_path, 
               interval_type='frames', 
               interval_value=60, 
               video_topic='general', 
               commentary_type='descriptive', 
               output_path=None, 
               speed_factor=1.15, 
               background_music=None, 
               tts_settings=None,
               **kwargs
               ):
        logger.info(f"Starting audio commentary generation for {video_path}")
        self.set_video(video_path)
        
        logger.info("Extracting frames")
        frames, timestamps, video_duration = extract_frames_fast(
            video_path, 
            interval_type, 
            interval_value,
            alwayse_include_last_fame=kwargs.get('alwayse_include_last_fame', True),
            **kwargs
        )
        logger.info(f"Frames extracted. Video duration: {video_duration}")

        logger.info("Generating timed commentary")
        self.comments = generate_timed_commentary(frames, timestamps, video_duration, video_topic, commentary_type)
        logger.info("Timed commentary generated")

        logger.info("Creating audio segments")
        tts = TextToSpeech(tts_settings) if tts_settings else TextToSpeech(TTSSettings())
        self.audio_segments = create_audio_segments(self.comments, tts)
        logger.info("Audio segments created")

        if output_path is None:
            output_path = self.project_folder / f"{self.video_name}_with_commentary.mp4"

        logger.info("Combining audio with video")
        combine_audio_with_video(
            video_path, 
            self.audio_segments, 
            self.comments.split('\n'), 
            output_path, 
            speed_factor, 
            background_music,
            **kwargs
        )
        self.final_video_path = output_path
        logger.info(f"Final video created at {self.final_video_path}")

        return {
            "comments": self.comments,
            "final_video_path": str(self.final_video_path)
        }

    def generate_textual_commentary(self, 
                                    video_path : str,
                                    video_topic :  str = 'general', 
                                    commentary_type : str ='detailed', 
                                    transcription: str = None, 
                                    **kwargs
                                    ):
        logger.info(f"Starting textual commentary generation for {video_path}")
        self.set_video(video_path)
        
        logger.info("Extracting frames")
        frames, timestamps, video_duration = extract_frames_fast(
            video_path, 
            **kwargs
        )
        logger.info(f"Frames extracted. Video duration: {video_duration}")

        logger.info("Generating untimed commentary")
        self.comments = generate_untimed_commentary(frames, video_topic, commentary_type, transcription, **kwargs)
        logger.info("Untimed commentary generated")

        return self.comments

    def save_state(self):
        state = {
            'video_name': self.video_name,
            'comments': self.comments,
            'final_video_path': str(self.final_video_path) if self.final_video_path else None
        }
        
        with open(self.project_folder / 'state.json', 'w') as f:
            json.dump(state, f)
        
        with open(self.project_folder / 'audio_segments.pkl', 'wb') as f:
            pickle.dump(self.audio_segments, f)

    def load_state(self, video_name):
        self.set_video(video_name)
        
        try:
            with open(self.project_folder / 'state.json', 'r') as f:
                state = json.load(f)
            
            self.video_name = state['video_name']
            self.comments = state['comments']
            self.final_video_path = Path(state['final_video_path']) if state['final_video_path'] else None
            
            with open(self.project_folder / 'audio_segments.pkl', 'rb') as f:
                self.audio_segments = pickle.load(f)
            
            return True
        except FileNotFoundError:
            print(f"No saved state found for video: {video_name}")
            return False

    def get_comments(self):
        return self.comments

    def get_audio_segments(self):
        return self.audio_segments

    def get_final_video_path(self):
        return self.final_video_path