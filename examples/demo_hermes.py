import os, sys
# append the parent directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from hermes.core import transcribe
from hermes.config import CONFIG

# Ensure GROQ_API_KEY is set
if not CONFIG['llm']['api_key']:
    raise ValueError("Please set the GROQ_API_KEY environment variable")

# Example 1: Basic transcription of a local file
print("Example 1: Basic transcription of a local file")
result = transcribe('examples/assets/input.mp4', provider='groq')
print(f"Transcription: {result['transcription'][:100]}...\n")

# Example 2: Transcription of a YouTube video
print("Example 2: Transcription of a YouTube video")
result = transcribe('https://www.youtube.com/watch?v=v=PNulbFECY-I', provider='groq')
print(f"Transcription: {result['transcription'][:100]}...\n")

# # Example 3: Transcription with a different model
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

print("All examples completed successfully!")