#!/bin/bash

# Define colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
RED='\033[0;31m'
NC='\033[0m'  # No Color

show_help() {
    printf "${CYAN}Usage:${NC} $0 <video-file> [provider: mlx | groq | openai] [model] [response_format for openai/groq] [additional-mlx-whisper-arguments]\n"
    printf "\n${GREEN}Hermes Video Transcription Script${NC}\n"
    printf "\n${CYAN}This script converts video to audio (mp3) and transcribes the audio using one of three providers: MLX, Groq, or OpenAI.${NC}\n"
    printf "\n${YELLOW}Positional Arguments:${NC}\n"
    printf "  video-file             The video file to be processed.\n"
    printf "\n${YELLOW}Optional Arguments:${NC}\n"
    printf "  provider               The transcription provider. Options are:\n"
    printf "                           mlx    - Uses mlx_whisper for transcription. Default model: distil-whisper-large-v3-en\n"
    printf "                           groq   - Uses Groq API for transcription. Default model: distil-whisper-large-v3-en\n"
    printf "                           openai - Uses OpenAI API for transcription. Default model: whisper-1\n"
    printf "\n  model                  The model to be used by the provider (optional).\n"
    printf "\n  response_format        Specifies the output format for Groq or OpenAI. Default: json\n"
    printf "                           Options: json, text, srt, verbose_json, vtt\n"
    printf "\n${YELLOW}Examples:${NC}\n"
    printf "  Basic usage with MLX (default):\n"
    printf "    ./hermes.sh input.mp4\n"
    printf "\n  Using Groq with default model:\n"
    printf "    ./hermes.sh input.mp4 groq\n"
    printf "\n  Using OpenAI with srt output:\n"
    printf "    ./hermes.sh input.mp4 openai whisper-1 srt\n"
}

transcribe_video() {
    local video_file="$1"
    local provider="${2:-mlx}"  # Default to mlx if not specified
    local model
    local response_format="vtt"  # Default response format for groq and openai is json
    # echo "response_format: $response_format"
    # Set default model based on provider
    if [ "$provider" == "groq" ]; then
        model="distil-whisper-large-v3-en"  # Default for Groq
    elif [ "$provider" == "openai" ]; then
        model="whisper-1"  # Default for OpenAI
    else
        model="distil-whisper-large-v3"  # Default for MLX
    fi

    # Iterate through arguments to check for --model
    while [[ $# -gt 0 ]]; do
        case $1 in
            --model)
                model="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
        case $1 in
            --response_format)
                response_format="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    echo "response_format: $response_format"

    # Remove the first four parameters, because they're not needed for the remaining execution
    shift 4

    printf "${CYAN}Converting video to mp3...${NC}\n"
    ffmpeg -loglevel error -i "$video_file" -ar 16000 -ac 1 -q:a 0 -map a "${video_file%.*}.mp3" -y
    printf "${GREEN}Conversion completed.${NC}\n"

    start_time=$(date +%s)
    if [ "$provider" == "groq" ]; then
        printf "${CYAN}Starting transcription with Groq using model: $model...${NC}\n"

        curl -X POST "https://api.groq.com/openai/v1/audio/transcriptions" \
             -H "Authorization: bearer $GROQ_API_KEY" \
             -F "file=@${video_file%.*}.mp3" \
             -F "model=$model" \
             -F "temperature=0" \
             -F "response_format=$response_format" \
             -F "language=en" > "${video_file%.*}_groq.$response_format"

    elif [ "$provider" == "openai" ]; then
        printf "${CYAN}Starting transcription with OpenAI using model: $model...${NC}\n"

        curl -X POST "https://api.openai.com/v1/audio/transcriptions" \
             -H "Authorization: Bearer $OPENAI_API_KEY" \
             -H "Content-Type: multipart/form-data" \
             -F "file=@${video_file%.*}.mp3" \
             -F "model=$model" \
             -F "response_format=$response_format" > "${video_file%.*}_openai.$response_format"

    else
        printf "${CYAN}Starting transcription with mlx_whisper using model: mlx-community/$model...${NC}\n"

        mlx_whisper "${video_file%.*}.mp3" --model "mlx-community/$model" --output-dir "./" "$@"
    fi

    end_time=$(date +%s) 
    duration_ns=$((end_time - start_time))

    # Output transcription time in seconds for capturing by the benchmark script
    printf "${GREEN}Transcription completed in $duration_ns seconds.${NC}\n"
    echo "TRANSCRIPTION_TIME=$duration_ns"

    rm "${video_file%.*}.mp3"
}

if [ "$1" == "-h" ]; then
    show_help
    exit 0
fi

if [ -z "$1" ]; then
    printf "${RED}Missing required arguments. Use -h for help.${NC}\n"
    exit 1
fi

transcribe_video "$@"
