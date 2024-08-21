# Hermes Video Transcription Script 🎥➡️📝

Hermes, the messenger of the gods, brings you lightning-fast video transcription! This script harnesses the power of cutting-edge AI to convert your videos into text with unprecedented speed and accuracy.

## 🚀 Features

- **Multi-Provider Support**: Choose from MLX Whisper, Groq, or OpenAI for transcription
- **Blazing Fast**: Transcribe a 393-second video in just 1 second with Groq's distil-whisper model!
- **Flexible**: Support for various models and output formats
- **Easy to Use**: Simple command-line interface for quick transcriptions

## 🏎️ Performance Comparison

![Hermes Benchmark Results](https://raw.githubusercontent.com/unclecode/hermes/main/assets/whisper-benchmark.png)

For a 393-second video:

| Provider | Model | Time (seconds) |
|----------|-------|----------------|
| Groq | distil-whisper-large-v3-en | 1 |
| Groq | whisper-large-v3 | 2 |
| MLX Whisper | distil-whisper-large-v3 | 11 |
| OpenAI | whisper-1 | 21 |

## 🛠️ Usage

#### IMPORTANT: Before you begin make sure your Groq api key is set in the environment variable `GROQ_API_KEY`. In case of OpenAI, set the environment variable `OPENAI_API_KEY`.

```bash
./hermes.sh <video-file> [provider: mlx | groq | openai] [model] [response_format] [additional-mlx-whisper-arguments]
```

### Examples:

0. Basic usage with MLX (default):
   ```bash
   ./hermes.sh input.mp4
   ```

1. Basic usage with MLX with different model:
   ```bash
   ./hermes.sh input.mp4 --model distil-whisper-large-v3
   ```

2. Using Groq with default model:
   ```bash
   ./hermes.sh input.mp4 groq
   ```

3. Using Groq with different model:
   ```bash
   ./hermes.sh input.mp4 groq --model whisper-large-v3
   ```

4. Using OpenAI with srt output:
   ```bash
   ./hermes.sh input.mp4 openai --model whisper-1 srt
   ```

## 📊 Running Benchmarks

Want to see how Hermes performs with different providers and models? Use our handy benchmark script to test transcription speeds on your own videos!

### Usage

```bash
./benchmark.sh <video-file>
```

This script will run the transcription process using all supported providers and models, then generate a performance report.

### Example

```bash
./benchmark.sh my_video.mp4
```

### What It Does

1. Runs transcription using:
   - MLX Whisper (distil-whisper-large-v3)
   - Groq (distil-whisper-large-v3-en)
   - Groq (whisper-large-v3)
   - OpenAI Whisper (whisper-1)
2. Measures the time taken for each transcription
3. Generates a report comparing the performance of each provider and model

### Sample Output

```
Benchmark Report for my_video.mp4
====================================
Video duration: 393.206689 seconds
MLX Whisper (distil-whisper-large-v3): 11 seconds
Groq (distil-whisper-large-v3-en): 1 seconds
Groq (whisper-large-v3): 2 seconds
OpenAI Whisper (whisper-1): 21 seconds
```

Run this benchmark on your own videos to see the impressive speed of Groq's distil-whisper model in action!

## 🌟 Why Hermes?

- **Speed**: Groq's distil-whisper model transcribes 393 seconds of audio in just 1 second!
- **Flexibility**: Choose the provider that best suits your needs
- **Local Option**: Use MLX Whisper for fast, local transcription on Mac or MPS systems
- **Cloud Power**: Leverage Groq's LPU for the fastest cloud-based transcription

## 🙏 Acknowledgements

Huge shoutout to the @GroqInc team for their incredible distil-whisper model, making ultra-fast transcription a reality!

## 🎉 Final Thoughts

We're living in amazing times! Whether you need the speed of Groq, the convenience of OpenAI, or the local power of MLX Whisper, Hermes has got you covered. Happy transcribing!