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

```bash
./hermes.sh <video-file> [provider: mlx | groq | openai] [model] [response_format] [additional-mlx-whisper-arguments]
```

### Examples:

1. Basic usage with MLX (default):
   ```bash
   ./hermes.sh input.mp4
   ```

2. Using Groq with default model:
   ```bash
   ./hermes.sh input.mp4 groq
   ```

3. Using OpenAI with srt output:
   ```bash
   ./hermes.sh input.mp4 openai whisper-1 srt
   ```

## 🌟 Why Hermes?

- **Speed**: Groq's distil-whisper model transcribes 393 seconds of audio in just 1 second!
- **Flexibility**: Choose the provider that best suits your needs
- **Local Option**: Use MLX Whisper for fast, local transcription on Mac or MPS systems
- **Cloud Power**: Leverage Groq's LPU for the fastest cloud-based transcription

## 🙏 Acknowledgements

Huge shoutout to the @GroqInc team for their incredible distil-whisper model, making ultra-fast transcription a reality!

## 🎉 Final Thoughts

We're living in amazing times! Whether you need the speed of Groq, the convenience of OpenAI, or the local power of MLX Whisper, Hermes has got you covered. Happy transcribing!