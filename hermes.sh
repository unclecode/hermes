#!/bin/bash

# Define colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
RED='\033[0;31m'
NC='\033[0m'  # No Color

show_help() {
    printf "${CYAN}Usage:${NC} $0 <video-file-or-youtube-url> [provider: mlx | groq | openai] [response_format] [model] [additional-mlx-whisper-arguments]\n"
    printf "\n${GREEN}Hermes Video Transcription Script${NC}\n"
    printf "\n${CYAN}This script converts video to audio (mp3), supports YouTube URLs, and transcribes the audio using one of three providers: MLX, Groq, or OpenAI.${NC}\n"
    printf "\n${YELLOW}Positional Arguments:${NC}\n"
    printf "  video-file-or-youtube-url  The video file or YouTube URL to be processed.\n"
    printf "\n${YELLOW}Optional Arguments:${NC}\n"
    printf "  provider               The transcription provider. Options are:\n"
    printf "                           mlx    - Uses mlx_whisper for transcription. Default model: distil-whisper-large-v3\n"
    printf "                           groq   - Uses Groq API for transcription. Default model: distil-whisper-large-v3-en\n"
    printf "                           openai - Uses OpenAI API for transcription. Default model: whisper-1\n"
    printf "\n  response_format        Specifies the output format. Default: vtt for mlx, text for others\n"
    printf "                           Options: json, text, srt, verbose_json, vtt\n"
    printf "\n  model                  The model to be used by the provider (optional).\n"
    printf "\n${YELLOW}Examples:${NC}\n"
    printf "  Basic usage with MLX (default):\n"
    printf "    $0 input.mp4\n"
    printf "\n  Using Groq with default model:\n"
    printf "    $0 input.mp4 groq\n"
    printf "\n  Using OpenAI with srt output:\n"
    printf "    $0 input.mp4 openai srt whisper-1\n"
    printf "\n  Processing a YouTube video:\n"
    printf "    $0 https://www.youtube.com/watch?v=v=PNulbFECY-I\n"
}

check_dependencies() {
    local deps=("yt-dlp" "ffmpeg" "mlx_whisper")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            printf "${RED}Error: $dep is not installed. Please install it and try again.${NC}\n"
            exit 1
        fi
    done
}

check_yt_dlp() {
    if ! command -v yt-dlp &> /dev/null
    then
        printf "${YELLOW}yt-dlp is not installed. This is required for YouTube video processing.${NC}\n"
        printf "${CYAN}To install yt-dlp, you can use one of the following methods:${NC}\n"
        printf "1. Using pip (Python package manager):\n"
        printf "   ${GREEN}pip install yt-dlp${NC}\n"
        printf "2. On macOS using Homebrew:\n"
        printf "   ${GREEN}brew install yt-dlp${NC}\n"
        printf "3. On Ubuntu or Debian:\n"
        printf "   ${GREEN}sudo apt-get install yt-dlp${NC}\n"
        printf "For other installation methods, please visit: https://github.com/yt-dlp/yt-dlp#installation\n"
        printf "${YELLOW}Please install yt-dlp and run the script again.${NC}\n"
        exit 1
    fi
}

get_video_duration() {
    local video_file="$1"
    ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$video_file"
}

download_youtube_audio() {
    check_yt_dlp

    local input="$1"
    local temp_file="temp_youtube_audio.mp3"
    local output_file="youtube_audio.mp3"
    local sample_rate=16000

    printf "${CYAN}Downloading audio from YouTube...${NC}\n"
    if yt-dlp -f 'bestaudio[ext=m4a]/bestaudio' \
              --extract-audio \
              --audio-format mp3 \
              --audio-quality 0 \
              -o "$temp_file" \
              "$input" > /dev/null 2>&1; then
        printf "${GREEN}YouTube audio download complete. Converting to 16kHz...${NC}\n"
        if ffmpeg -i "$temp_file" -ar $sample_rate -ac 1 -q:a 0 "$output_file" -y > /dev/null 2>&1; then
            printf "${GREEN}Conversion to 16kHz completed: $output_file${NC}\n"
            rm -f "$temp_file"
            echo "$output_file"
        else
            printf "${RED}Failed to convert audio to 16kHz. Please check ffmpeg installation.${NC}\n"
            rm -f "$temp_file"
            return 1
        fi
    else
        printf "${RED}Failed to download YouTube audio. Please check the URL and try again.${NC}\n"
        return 1
    fi
}

transcribe_video() {
    local input="$1"
    local provider="${2:-groq}"
    local model
    local response_format
    local audio_file

    # Set default model and response format based on provider
    if [ "$provider" == "groq" ]; then
        model="${4:-distil-whisper-large-v3-en}"
        response_format="${3:-text}"
    elif [ "$provider" == "openai" ]; then
        model="${4:-whisper-1}"
        response_format="${3:-text}"
    elif [ "$provider" == "mlx" ]; then
        model="${4:-distil-whisper-large-v3}"
        response_format="${3:-vtt}"
    else
        # Set to groq as default provider
        provider="groq"
        model="${4:-distil-whisper-large-v3-en}"
        response_format="${3:-text}"
    fi

    # Check if input is a YouTube URL
    if [[ "$input" == http*youtube.com* ]] || [[ "$input" == http*youtu.be* ]] || [[ "$input" == http*youtube.com/shorts* ]]; then
        download_youtube_audio "$input"
        audio_file="youtube_audio.mp3"
        if [ $? -ne 0 ] || [ -z "$audio_file" ]; then
            printf "${RED}Failed to process YouTube audio. Exiting.${NC}\n"
            exit 1
        fi
    else
        # Convert local video to mp3
        audio_file="${input%.*}_temp.mp3"
        printf "${CYAN}Converting video to mp3...${NC}\n"
        if ! ffmpeg -loglevel error -i "$input" -ar 16000 -ac 1 -q:a 0 -map a "$audio_file" -y; then
            printf "${RED}Failed to convert video to audio. Please check the input file.${NC}\n"
            exit 1
        fi
        printf "${GREEN}Conversion completed.${NC}\n"
    fi

    start_time=$(date +%s)
    if [ "$provider" == "groq" ]; then
        printf "${CYAN}Starting transcription with Groq using model: $model...${NC}\n"
        if [ -z "$GROQ_API_KEY" ]; then
            printf "${RED}Error: GROQ_API_KEY is not set. Please set it and try again.${NC}\n"
            exit 1
        fi
        curl -X POST "https://api.groq.com/openai/v1/audio/transcriptions" \
             -H "Authorization: bearer $GROQ_API_KEY" \
             -F "file=@$audio_file" \
             -F "model=$model" \
             -F "temperature=0" \
             -F "response_format=$response_format" \
             -F "language=en" > "${input##*/}_groq.$response_format"

    elif [ "$provider" == "openai" ]; then
        printf "${CYAN}Starting transcription with OpenAI using model: $model...${NC}\n"
        if [ -z "$OPENAI_API_KEY" ]; then
            printf "${RED}Error: OPENAI_API_KEY is not set. Please set it and try again.${NC}\n"
            exit 1
        fi
        curl -X POST "https://api.openai.com/v1/audio/transcriptions" \
             -H "Authorization: Bearer $OPENAI_API_KEY" \
             -H "Content-Type: multipart/form-data" \
             -F "file=@$audio_file" \
             -F "model=$model" \
             -F "response_format=$response_format" > "${input##*/}_openai.$response_format"

    else
        printf "${CYAN}Starting transcription with mlx_whisper using model: mlx-community/$model...${NC}\n"
        mlx_whisper "$audio_file" --model "mlx-community/$model" --output-dir "./" "${@:5}"
    fi

    end_time=$(date +%s) 
    duration_ns=$((end_time - start_time))

    local duration=$(get_video_duration "$audio_file")
    printf "${YELLOW}Audio duration: ${duration} seconds${NC}\n"

    # Output transcription time in seconds for capturing by the benchmark script
    printf "${GREEN}Transcription completed in $duration_ns seconds.${NC}\n"
    echo "TRANSCRIPTION_TIME=$duration_ns"

    # Clean up the audio file
    rm -f "$audio_file"
}

# Main script execution
check_dependencies

if [ "$1" == "-h" ]; then
    show_help
    exit 0
fi

if [ -z "$1" ]; then
    printf "${RED}Missing required arguments. Use -h for help.${NC}\n"
    exit 1
fi

transcribe_video "$@"