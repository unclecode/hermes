#!/bin/bash

# Define colors
GREEN='\033[0;32m'
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'  # No Color

# Function to get video duration
get_video_duration() {
    local video_file="$1"
    ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$video_file"
}

# Function to run the benchmark
run_benchmark() {
    local video_file="$1"
    local report_file="benchmark_report.txt"
    
    # Get video duration
    local duration=$(get_video_duration "$video_file")
    echo -e "${YELLOW}Video duration: ${duration} seconds${NC}"
    
    # Initialize the report
    echo -e "${YELLOW}Benchmarking started for $video_file...${NC}"
    echo "Benchmark Report for $video_file" > "$report_file"
    echo "==================================" >> "$report_file"
    echo "Video duration: ${duration} seconds" >> "$report_file"
    
    # MLX Benchmark
    echo -e "${CYAN}Running MLX Whisper benchmark...${NC}"
    mlx_output=$(./hermes.sh "$video_file" mlx)
    mlx_time=$(echo "$mlx_output" | grep 'TRANSCRIPTION_TIME' | cut -d '=' -f 2)
    echo -e "${GREEN}MLX completed in $mlx_time seconds.${NC}"
    echo "MLX Whisper (distil-whisper-large-v3): $mlx_time seconds" >> "$report_file"
    
    # Groq Benchmark (distil-whisper-large-v3)
    echo -e "${CYAN}Running Groq benchmark (distil-whisper-large-v3-en)...${NC}"
    groq_output=$(./hermes.sh "$video_file" groq)
    groq_distil_time=$(echo "$groq_output" | grep 'TRANSCRIPTION_TIME' | cut -d '=' -f 2)
    echo -e "${GREEN}Groq (distil-whisper-large-v3-en) completed in $groq_distil_time seconds.${NC}"
    echo "Groq (distil-whisper-large-v3-en): $groq_distil_time seconds" >> "$report_file"

    # Groq Benchmark (whisper-large-v3)
    echo -e "${CYAN}Running Groq benchmark (whisper-large-v3)...${NC}"
    groq_large_output=$(./hermes.sh "$video_file" groq --model whisper-large-v3)
    groq_large_time=$(echo "$groq_large_output" | grep 'TRANSCRIPTION_TIME' | cut -d '=' -f 2)
    echo -e "${GREEN}Groq (whisper-large-v3) completed in $groq_large_time seconds.${NC}"
    echo "Groq (whisper-large-v3): $groq_large_time seconds" >> "$report_file"
    
    # OpenAI Benchmark
    echo -e "${CYAN}Running OpenAI Whisper benchmark...${NC}"
    openai_output=$(./hermes.sh "$video_file" openai --model whisper-1)
    openai_time=$(echo "$openai_output" | grep 'TRANSCRIPTION_TIME' | cut -d '=' -f 2)
    echo -e "${GREEN}OpenAI completed in $openai_time seconds.${NC}"
    echo "OpenAI Whisper (whisper-1): $openai_time seconds" >> "$report_file"
    
    # Final Report
    echo -e "${YELLOW}Benchmarking completed. Generating report...${NC}"
    # echo -e "\nBenchmark Results:" >> "$report_file"
    # echo "==================================" >> "$report_file"
    # echo "MLX Whisper (distil-whisper-large-v3): $mlx_time seconds" >> "$report_file"
    # echo "Groq (distil-whisper-large-v3-en): $groq_distil_time seconds" >> "$report_file"
    # echo "Groq (whisper-large-v3): $groq_large_time seconds" >> "$report_file"
    # echo "OpenAI Whisper (whisper-1): $openai_time seconds" >> "$report_file"

    echo -e "${GREEN}Report generated in $report_file${NC}"

    # Display the content of the report file
    echo -e "\n${YELLOW}Benchmark Report:${NC}"
    cat "$report_file"
}

# Check if video file is provided
if [ -z "$1" ]; then
    echo -e "${RED}Usage: $0 <video-file>${NC}"
    exit 1
fi

# Run the benchmark
run_benchmark "$1"
