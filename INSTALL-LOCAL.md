# unclecode/hermes (video transcription) — local install

**Not** Nous Research Hermes Agent. Different product, same common name.

## Layout
- Clone + optional venv: this repository root
- Config/cache: `~/.unclecode-hermes/` (never `~/.hermes` or `%LOCALAPPDATA%/hermes`)
- CLIs after install: `unclecode-hermes`, `uhermes`
- Optional launchers: `unclecode-hermes.bat` / `unclecode-hermes.sh` in the repo root

## Install (editable)
```bash
python -m venv .venv
# Windows
.venv\Scripts\pip install -e .
# Unix
.venv/bin/pip install -e .
```

## Run
```bash
unclecode-hermes path/to/video.mp4 -p groq
unclecode-hermes https://www.youtube.com/watch?v=VIDEO_ID -p groq -o out.txt
```

Providers: `groq` (default), `openai`, `mlx` (Mac/MPS only).

## Config
Edit `~/.unclecode-hermes/config.yml` (or `config.yaml`) or set env:
- `GROQ_API_KEY`
- `OPENAI_API_KEY`
- optional home override: `UNCLECODE_HERMES_HOME`

## Optional extras
```bash
pip install -e ".[audio]"   # mic path (sounddevice / PortAudio)
pip install -e ".[mlx]"     # Mac/MPS local whisper
pip install -e ".[all]"
```

## Isolation / safety
- Package console scripts are `unclecode-hermes` / `uhermes` only (no `hermes` entry point)
- Config home is `~/.unclecode-hermes`
- Lazy config load (no import-time API key hard-fail)
- `sounddevice` is an optional import
- Post-install never writes under agent `~/.hermes`
