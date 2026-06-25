# Hermes v0.1.0: Lightning-Fast Video Transcription 🎥➡️📝

![Hermes Benchmark Results](https://raw.githubusercontent.com/unclecode/hermes/main/assets/whisper-benchmark.png)


[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1taJvfZKgTxOtScaMR3qofj-ev_8nwn9P?usp=sharing)

Hermes, the messenger of the gods, now brings you ultra-fast video transcription powered by cutting-edge AI! This Python library and CLI tool harnesses the speed of Groq and the flexibility of multiple providers to convert your videos into text with unprecedented efficiency.

## 🚀 Features

- **Blazing Fast**: Transcribe a 393-second video in just 1 second with Groq's distil-whisper model!
- **Multi-Provider Support**: Choose from Groq (default), MLX Whisper, OpenAI, or TwelveLabs Pegasus for transcription
- **Video-Native Understanding**: TwelveLabs Pegasus reads the *video* itself (not just the audio track), using on-screen text and visual context to sharpen the transcript
- **YouTube Support**: Easily transcribe YouTube videos by simply passing the URL
- **Flexible**: Support for various models and output formats
- **Python Library & CLI**: Use Hermes in your Python projects or directly from the command line
- **LLM Processing**: Process the transcription with an LLM for further analysis

## 📦 Installation

### Prerequisites for Colab or Ubuntu-like Systems

If you're using Google Colab or a Linux system like Ubuntu, you need to install some additional dependencies first. Run the following command:

```
!apt install libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg
```

### Installing Hermes

You can install Hermes directly from GitHub using pip. There are two installation options:

#### Standard Installation (without MLX support)

For most users, the standard installation without MLX support is recommended:

```
pip install git+https://github.com/unclecode/hermes.git@main
```

This installation includes all core features but excludes MLX-specific functionality.

#### Installation with MLX Support

If you're using a Mac or an MPS system and want to use MLX Whisper for local transcription, install Hermes with MLX support:

```
pip install git+https://github.com/unclecode/hermes.git@main#egg=hermes[mlx]
```

This installation includes all core features plus MLX Whisper support for local transcription.

**Note:** MLX support is currently only available for Mac or MPS systems. If you're unsure which version to install, start with the standard installation.

## ⚙️ Configuration

Hermes uses a configuration file to manage its settings. On first run, Hermes will automatically create a `.hermes` folder in your home directory and populate it with a default `config.yml` file.

You can customize Hermes' behavior by editing this file. Here's an example of what the `config.yml` might look like:

```yaml
# LLM (Language Model) settings
llm:
  provider: groq
  model: llama-3.1-8b-instant
  api_key: your_groq_api_key_here

# Transcription settings
transcription:
  provider: groq
  model: distil-whisper-large-v3-en
  api_key: your_groq_api_key_here

# Cache settings
cache:
  enabled: true
  directory: ~/.hermes/cache

# Source type for input (auto-detect by default)
source_type: auto
```

The configuration file is located at `~/.hermes/config.yml`. You can edit this file to change providers, models, API keys, and other settings.

**Note:** If you don't specify API keys in the config file, Hermes will look for them in your environment variables. For example, it will look for `GROQ_API_KEY` if you're using Groq as a provider, or `TWELVELABS_API_KEY` for TwelveLabs.

### Using TwelveLabs Pegasus

[TwelveLabs](https://twelvelabs.io) Pegasus is a video-understanding model. Unlike the Whisper-based providers, it analyzes the video directly, so it can lean on visual context and on-screen text when producing a transcript.

The provider is optional. Install it with:

```
pip install "git+https://github.com/unclecode/hermes.git@main#egg=hermes[twelvelabs]"
```

Set your API key (a free key is available at [twelvelabs.io](https://twelvelabs.io)):

```
export TWELVELABS_API_KEY=your_key_here
```

Then select the provider:

```python
result = transcribe('path/to/your/video.mp4', provider='twelvelabs')
print(result['transcription'])
```

```
hermes path/to/your/video.mp4 -p twelvelabs
```

Public video URLs are analyzed in place; local files (and YouTube/microphone sources) are uploaded to TwelveLabs as an asset before analysis. You can override the model (default `pegasus1.5`) with `-m`/`model=`.

To override the configuration temporarily, you can also use command-line arguments when running Hermes. These will take precedence over the settings in the config file.

## 🛠️ Usage

### Python Library

1. Basic transcription:

```python
from hermes import transcribe

result = transcribe('path/to/your/video.mp4', provider='groq')
print(result['transcription'])
```

2. Transcribe a YouTube video:

```python
result = transcribe('https://www.youtube.com/watch?v=v=PNulbFECY-I', provider='groq')
print(result['transcription'])
```

3. Use a different model:

```python
result = transcribe('path/to/your/video.mp4', provider='groq', model='whisper-large-v3')
print(result['transcription'])
```

4. Get JSON output:

```python
result = transcribe('path/to/your/video.mp4', provider='groq', response_format='json')
print(result['transcription'])
```

5. Process with LLM:

```python
result = transcribe('path/to/your/video.mp4', provider='groq', llm_prompt="Summarize this transcription in 3 bullet points")
print(result['llm_processed'])
```

### Command Line Interface

1. Basic usage:

```
hermes path/to/your/video.mp4 -p groq
```

2. Transcribe a YouTube video:

```
hermes https://www.youtube.com/watch?v=v=PNulbFECY-I -p groq
```

3. Use a different model:

```
hermes path/to/your/video.mp4 -p groq -m whisper-large-v3
```

4. Get JSON output:

```
hermes path/to/your/video.mp4 -p groq --response_format json
```

5. Process with LLM:

```
hermes path/to/your/video.mp4 -p groq --llm_prompt "Summarize this transcription in 3 bullet points"
```

## 🏎️ Performance Comparison

![Hermes Benchmark Results](https://raw.githubusercontent.com/unclecode/hermes/main/assets/whisper-benchmark.png)

For a 393-second video:

| Provider | Model | Time (seconds) |
|----------|-------|----------------|
| Groq | distil-whisper-large-v3-en | 1 |
| Groq | whisper-large-v3 | 2 |
| MLX Whisper | distil-whisper-large-v3 | 11 |
| OpenAI | whisper-1 | 21 |

## 📊 Running Benchmarks

Test Hermes performance with different providers and models:

```
python -m hermes.benchmark path/to/your/video.mp4
```

or

```
python -m hermes.benchmark https://www.youtube.com/watch?v=v=PNulbFECY-I
```

This will generate a performance report for all supported providers and models.

## 🌟 Why Hermes?

- **Unmatched Speed**: Groq's distil-whisper model transcribes 393 seconds of audio in just 1 second!
- **Flexibility**: Choose the provider that best suits your needs
- **Easy Integration**: Use as a Python library or CLI tool
- **YouTube Support**: Transcribe YouTube videos without manual downloads
- **Local Option**: Use MLX Whisper for fast, local transcription on Mac or MPS systems
- **Cloud Power**: Leverage Groq's LPU for the fastest cloud-based transcription

## 🙏 Acknowledgements

Huge shoutout to the @GroqInc team for their incredible distil-whisper model, making ultra-fast transcription a reality!

## 🎉 Final Thoughts

We're living in amazing times! Whether you need the lightning speed of Groq, the convenience of OpenAI, the local power of MLX Whisper, or the video-native understanding of TwelveLabs Pegasus, Hermes has got you covered. Happy transcribing!