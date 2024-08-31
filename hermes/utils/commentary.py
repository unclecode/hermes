import cv2
import base64
import json, math
import webvtt
from litellm import completion
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import tempfile
import os
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip, TextClip
from moviepy.video.tools.subtitles import SubtitlesClip
from pydub import AudioSegment
from ..config import CONFIG

def extract_frames(video_path, interval_type='frames', interval_value=60):
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    frames = []
    timestamps = []
    frame_count = 0
    
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        
        frame_count += 1
        if interval_type == 'frames' and frame_count % interval_value == 0:
            frames.append(process_frame(frame))
            timestamps.append(video.get(cv2.CAP_PROP_POS_MSEC) / 1000)
        elif interval_type == 'seconds' and frame_count % int(fps * interval_value) == 0:
            frames.append(process_frame(frame))
            timestamps.append(video.get(cv2.CAP_PROP_POS_MSEC) / 1000)
    
    video.release()
    return frames, timestamps

def resize_frame(frame, target_size):
    h, w = frame.shape[:2]
    aspect_ratio = w / h
    if aspect_ratio > 1:
        # Width is larger, so scale based on width
        new_w = target_size
        new_h = int(new_w / aspect_ratio)
    else:
        # Height is larger or equal, so scale based on height
        new_h = target_size
        new_w = int(new_h * aspect_ratio)
    return cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)


def extract_frames_fast(video_path, interval_type='seconds', interval_value=6, snapshot_count = 5, target_size=320, alwayse_include_last_frame = True, **kwargs):
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    total_duration = total_frames / fps
    frames = []
    timestamps = []
    
    if interval_type == 'frames':
        frame_indices = range(0, total_frames, interval_value)
    elif interval_type == 'seconds':
        frame_indices = range(0, total_frames, int(fps * interval_value))
    elif interval_type == 'total_snapshots':
        if snapshot_count <= 0:
            raise ValueError("snapshot_count must be positive for 'total_snapshots' mode")
        snapshot_interval = total_frames // snapshot_count
        frame_indices = range(0, total_frames, snapshot_interval)
    else:
        raise ValueError("Invalid interval_type. Choose 'frames', 'seconds', or 'total_snapshots'")
    
    for frame_index in frame_indices:
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        success, frame = video.read()
        if not success:
            break
        
        if target_size:
            frame = resize_frame(frame, target_size)
        
        frames.append(process_frame(frame))
        timestamps.append(video.get(cv2.CAP_PROP_POS_MSEC) / 1000)
        
    if alwayse_include_last_frame and frame_index != total_frames - 1:
        video.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
        success, frame = video.read()
        if success:
            if target_size:
                frame = resize_frame(frame, target_size)
            frames.append(process_frame(frame))
            timestamps.append(video.get(cv2.CAP_PROP_POS_MSEC) / 1000)
    
    video.release()
    return frames, timestamps, total_duration

def process_frame(frame):
    # Placeholder for any additional processing
    # For example, you might want to convert to RGB if working with PIL later
    # return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return frame

def process_frame(frame):
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")

def estimate_word_counts(timestamps, video_duration):
    # Constants
    slow_speech_rate = 130  # words per minute (slower than average)
    words_per_second = slow_speech_rate / 60
    safety_factor = 0.9  # Further reduce to account for pauses, emphasis, etc.
    
    # Calculate intervals
    intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
    intervals.append(video_duration - timestamps[-1])
    
    # Calculate word counts
    word_counts = []
    for interval in intervals:
        # Estimate words that can fit in this interval
        estimated_words = math.floor(interval * words_per_second * safety_factor)
        
        # Ensure a minimum of 1 word per interval
        words = max(1, estimated_words)
        
        word_counts.append(words)
    
    return word_counts

def generate_timed_commentary(frames, timestamps, video_duration, video_topic, commentary_type, **kwargs):
    frame_data = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame}"}} for frame in frames]
    word_counts = estimate_word_counts(timestamps, video_duration)
    
    prompt_content = [
        {"type": "text", "text": f"These are frames from a {video_topic} video with their corresponding timestamps in seconds. Create a {commentary_type} commentary with precise timestamps. Format each comment as 'timestamp: comment'. Ensure comments align with specific moments in the video and adhere to the specified word count for each interval. **Make sure you generate same number of words as given here, no more nor less.** **Also do not choose words with more than 3 syllables.** Make sure to follow exact format of 'timestamp: comment'. Timestamp is a floating point number, and no extra new lines are allowed."},
        {"type": "text", "text": "Timestamps and word counts:"}
    ]
    
    for i, (timestamp, word_count) in enumerate(zip(timestamps, word_counts)):
        prompt_content.append({"type": "text", "text": f"Timestamp {timestamp:.2f}: {word_count} words"})
    
    prompt_content.extend(frame_data)
    
    try:
        response = completion(
            model=CONFIG['commentary']['model'],
            messages=[{"role": "user", "content": prompt_content}],
            max_tokens=4000
        )
        
        comments = response.choices[0].message.content.split('\n')
        if kwargs.get('always_keep_last_frame', True):
            # Merge the last comment with the previous one
            comments[-2] = comments[-2].strip() + ' ' + comments[-1].strip().split(': ', 1)[1]
            
        return '\n'.join(comments[:-1])
    except Exception as e:
        print(f"Error generating commentary: {e}")
        return ""

def generate_untimed_commentary(frames, video_topic, commentary_type, transcription=None, **kwargs):
    frame_data = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame}"}} for frame in frames]
    
    prompt_content = [
        {"type": "text", "text": f"These are frames from a {video_topic} video. Create a {commentary_type} commentary describing everything you see in detail. Focus on extracting as much information as possible from the visual content."}
    ]
    
    if transcription:
        prompt_content.append({"type": "text", "text": f"Here's the video transcription to enrich your commentary:\n{transcription}"})
    
    prompt_content.extend(frame_data)
    
    response = completion(
        model=CONFIG['commentary']['model'],
        messages=[{"role": "user", "content": prompt_content}],
        max_tokens=4000
    )
    
    return response.choices[0].message.content

def create_audio_segments(commentary, tts, **kwargs):
    audio_segments = []
    
    def process_line(line):
        if not line:
            return None
        timestamp, text = line.split(': ', 1)
        timestamp = re.findall(r"[-+]?\d*\.\d+|\d+", timestamp)[0]
        
        audio_file_path = tts.generate_audio(text)
        
        audio_segment = AudioSegment.from_mp3(audio_file_path)
        os.unlink(audio_file_path)  # Remove the temporary file
        
        return (float(timestamp), audio_segment)

    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_line = {executor.submit(process_line, line): line for line in commentary.split('\n') if line}
        for future in as_completed(future_to_line):
            result = future.result()
            if result:
                audio_segments.append(result)

    audio_segments.sort(key=lambda x: x[0])
    return audio_segments


def calculate_new_dimensions(video, output_size):
    """
    Calculate new dimensions based on the given output_size while preserving aspect ratio.
    If only width or height is provided, calculate the other dimension.
    """
    if isinstance(output_size, tuple) and len(output_size) == 2:
        return output_size
    elif isinstance(output_size, (int, float)) or (isinstance(output_size, tuple) and len(output_size) == 1):
        if isinstance(output_size, tuple):
            output_size = output_size[0]
        aspect_ratio = video.w / video.h
        if video.w > video.h:
            return (int(output_size), int(output_size / aspect_ratio))
        else:
            return (int(output_size * aspect_ratio), int(output_size))
    else:
        raise ValueError("Invalid output_size. Provide either (width, height) or (width,) or a single number.")



def combine_audio_with_video(video_path, audio_segments, comments, output_path, speed_factor=1.15, background_music=None, video_output_size=(640,), **kwargs):
    video = VideoFileClip(video_path)
    audio_clips = []
    subtitles = []

    fps = video.fps if video.fps and video.fps > 0 else 30
    fps = float(fps)

    # Resize video if output_size is specified
    if video_output_size:
        new_size = calculate_new_dimensions(video, video_output_size)
        video = video.resize(newsize=new_size)

    with tempfile.TemporaryDirectory() as temp_dir:
        first_timestamp = audio_segments[0][0]
        time_adjustment = -first_timestamp

        for i, ((timestamp, segment), comment) in enumerate(zip(audio_segments, comments)):
            segment = segment.speedup(playback_speed=speed_factor)
            
            temp_audio_path = os.path.join(temp_dir, f"temp_audio_{i}.wav")
            segment.export(temp_audio_path, format="wav")
            
            adjusted_timestamp = max(0, timestamp + time_adjustment)
            
            audio_clip = AudioFileClip(temp_audio_path).set_start(adjusted_timestamp)
            audio_clips.append(audio_clip)

            subtitles.append(((adjusted_timestamp, adjusted_timestamp + audio_clip.duration), comment.split(': ', 1)[1]))

        commentary_audio = CompositeAudioClip(audio_clips)
        
        if background_music:
            bg_music = background_music.prepare_for_video(video.duration)
            final_audio = CompositeAudioClip([commentary_audio, bg_music])
        else:
            final_audio = commentary_audio

        final_audio = final_audio.set_duration(video.duration)

        # Adjust fontsize based on video size
       # Define a minimum font size to avoid too small text
        min_fontsize = 18

        # Adjust fontsize based on video size with a minimum threshold
        fontsize = max(int(video.w * 24 / 1920), min_fontsize)

        # Create the subtitle clip with the adjusted fontsize
        subtitle_clip = SubtitlesClip(subtitles, lambda txt: TextClip(
            txt,
            fontsize=fontsize,
            font='Arial-Black',  # Use a thicker font like 'Arial-Black'
            color='white',
            method='caption',  # Use caption method to handle wrapping
            size=(video.w, None)  # Set size to the video width to handle wrapping
        ))
        
        final_video = CompositeVideoClip([video, subtitle_clip.set_position(('center', 'bottom'))])
        final_video = final_video.set_audio(final_audio)
        final_video = final_video.set_fps(fps)

        final_video.write_videofile(
            str(output_path),
            fps=fps,
            ffmpeg_params=['-strict', '-2'],
            audio=True
        )

    video.close()
    final_video.close()
    for clip in audio_clips:
        clip.close()

def save_commentary(commentary, output_format='json', filename='commentary'):
    comments = []
    for line in commentary.split('\n'):
        if line.strip():
            parts = line.split(': ', 1)
            if len(parts) == 2:
                timestamp, comment = parts
                comments.append({"start": float(timestamp), "text": comment})
            else:
                comments.append({"text": line.strip()})

    if output_format == 'json':
        with open(f'{filename}.json', 'w') as f:
            json.dump(comments, f, indent=2)
    elif output_format == 'vtt':
        vtt = webvtt.WebVTT()
        for i, comment in enumerate(comments):
            if 'start' in comment:
                start = webvtt.seconds_to_timestamp(comment['start'])
                end = webvtt.seconds_to_timestamp(comments[i+1]['start'] if i+1 < len(comments) and 'start' in comments[i+1] else comment['start'] + 5)
                vtt.captions.append(webvtt.Caption(start, end, comment['text']))
            else:
                vtt.captions.append(webvtt.Caption('00:00:00', '00:00:05', comment['text']))
        vtt.save(f'{filename}.vtt')
    elif output_format == 'text':
        with open(f'{filename}.txt', 'w') as f:
            for comment in comments:
                if 'start' in comment:
                    f.write(f"{comment['start']:.2f}: {comment['text']}\n")
                else:
                    f.write(f"{comment['text']}\n")
    else:
        raise ValueError("Unsupported output format. Use 'json', 'vtt', or 'text'.")