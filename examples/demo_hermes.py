import os, sys
# append the parent directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from hermes.core import transcribe, Hermes
from hermes.config import CONFIG

# Ensure GROQ_API_KEY is set
if not CONFIG['llm']['api_key']:
    raise ValueError("Please set the GROQ_API_KEY environment variable")

hermes = Hermes()

# Example 1: Basic transcription of a local file
print("Example 1: Basic transcription of a local file")
result = transcribe('examples/assets/input.mp4', provider='groq')
print(f"Transcription: {result['transcription'][:100]}...\n")

# Example 2: Transcription of a YouTube video
print("Example 2: Transcription of a YouTube video")
result = transcribe('https://www.youtube.com/watch?v=v=PNulbFECY-I', provider='groq')
print(f"Transcription: {result['transcription'][:100]}...\n")

# Example 3: Transcription with a different model
print("Example 3: Transcription with a different model")
result = transcribe('examples/assets/input.mp4', provider='groq', model='whisper-large-v3')
print(f"Transcription: {result['transcription'][:100]}...\n")

# Example 4: Transcription with a different response format
print("Example 4: Transcription with a different response format")
result = transcribe('examples/assets/input.mp4', provider='groq', response_format='json')
print(f"JSON Response: {result['transcription']}\n")

# Example 5: Transcription with LLM processing
print("Example 5: Transcription with LLM processing")
result = transcribe('examples/assets/input.mp4', provider='groq', llm_prompt='Summarize this transcription in 3 bullet points')
print(f"Transcription: {result['transcription'][:100]}...")
print(f"LLM Summary: {result['llm_processed']}\n")

# Example 6: Forced transcription (bypassing cache)
print("Example 6: Forced transcription (bypassing cache)")
result = transcribe('examples/assets/input.mp4', provider='groq', force=True)
print(f"Transcription: {result['transcription'][:100]}...\n")

# Example 7: Generate video commentary for a local file
print("Example 7: Generate video commentary for a local file")
result = hermes.generate_video_commentary('examples/assets/input_football.mp4', force = True, interval_type = "total_snapshots", interval_value=6, target_size=224, video_output_size=(640,))
print(f"Commentary: {result['commentary'][:100]}...")
print(f"Final video path: {result['final_video_path']}\n")

# Example 8: Generate video commentary for a YouTube video
print("Example 8: Generate video commentary for a YouTube video")
result = hermes.generate_video_commentary('https://www.youtube.com/watch?v=v=PNulbFECY-I')
print(f"Commentary: {result['commentary'][:100]}...")
print(f"Final video path: {result['final_video_path']}\n")

# Example 9: Generate textual commentary for a local file
print("Example 9: Generate textual commentary for a local file")
result = hermes.generate_textual_commentary('examples/assets/input_football.mp4')
print(f"Textual Commentary: {result['textual_commentary'][:100]}...\n")

# Example 10: Generate textual commentary for a YouTube video with LLM processing
print("Example 10: Generate textual commentary for a YouTube video with LLM processing")
result = hermes.generate_textual_commentary(
    'examples/assets/input_football.mp4',
    llm_prompt='Make a short story out of this commentary'
)
print(f"Textual Commentary: {result['textual_commentary'][:100]}...")
print(f"LLM Summary: {result['llm_processed']}\n")

print("All examples completed successfully!")