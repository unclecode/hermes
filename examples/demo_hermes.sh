#!/bin/bash

# Ensure GROQ_API_KEY is set
if [ -z "$GROQ_API_KEY" ]; then
    echo "Please set the GROQ_API_KEY environment variable"
    exit 1
fi

# Example 1: Basic transcription of a local file
echo "Example 1: Basic transcription of a local file"
python -m hermes.cli examples/assets/input.mp4 -p groq

# Example 2: Transcription of a YouTube video
echo -e "\nExample 2: Transcription of a YouTube video"
python -m hermes.cli https://www.youtube.com/watch?v=PNulbFECY-I -p groq

# Example 3: Transcription with a different model
echo -e "\nExample 3: Transcription with a different model"
python -m hermes.cli examples/assets/input.mp4 -p groq -m whisper-large-v3

# Example 4: Transcription with a different response format
echo -e "\nExample 4: Transcription with a different response format"
python -m hermes.cli examples/assets/input.mp4 -p groq --response_format json

# Example 5: Transcription with LLM processing
echo -e "\nExample 5: Transcription with LLM processing"
python -m hermes.cli examples/assets/input.mp4 -p groq --llm_prompt "Summarize this transcription in 3 bullet points"

# Example 6: Forced transcription (bypassing cache)
echo -e "\nExample 6: Forced transcription (bypassing cache)"
python -m hermes.cli examples/assets/input.mp4 -p groq -f

# Example 7: Generate Video/Audio commentary
python -m hermes.cli input_football.mp4 --generate-commentary --interval-type total_snapshots --snapshot-count 8

# Example 8: Generate Textual commentary
python -m hermes.cli input_football.mp4 --textual-commentary --interval-type seconds --interval-value 10 --llm_prompt "Summarize the video content"

echo -e "\nAll examples completed successfully!"