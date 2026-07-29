from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
from pathlib import Path

# Read requirements.txt — drop Mac-only mlx; keep mic deps optional on Windows
with open("requirements.txt", encoding="utf-8") as f:
    requirements = [
        req
        for req in f.read().splitlines()
        if req.strip()
        and not req.strip().startswith("#")
        and not req.startswith("mlx-")
    ]

optional_audio = []
core_requirements = []
for req in requirements:
    name = req.split(">=")[0].split("==")[0].strip().lower()
    if name in {"pyaudio", "sounddevice"}:
        optional_audio.append(req)
    else:
        core_requirements.append(req)

mlx_requirements = ["mlx-whisper>=0.3.0"]

DEFAULT_CONFIG_YAML = """\
llm:
  provider: groq
  model: llama-3.1-8b-instant
  api_key: null
transcription:
  provider: groq
  model: distil-whisper-large-v3-en
  api_key: null
cache:
  enabled: true
  directory: {cache_dir}
source_type: auto
"""


def post_install():
    # NEVER touch ~/.hermes — that namespace is used by Nous Hermes Agent on this machine.
    hermes_dir = Path.home() / ".unclecode-hermes"
    hermes_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = hermes_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    for name in ("config.yml", "config.yaml"):
        if (hermes_dir / name).exists():
            return
    config_path = hermes_dir / "config.yml"
    # Write plain YAML without importing PyYAML at build/install setup time.
    text = DEFAULT_CONFIG_YAML.format(cache_dir=str(cache_dir).replace("\\", "/"))
    config_path.write_text(text, encoding="utf-8")


class PostInstallCommand(install):
    def run(self):
        install.run(self)
        post_install()


class PostDevelopCommand(develop):
    def run(self):
        develop.run(self)
        post_install()


setup(
    name="unclecode-hermes",
    version="0.1.0",
    packages=find_packages(),
    install_requires=core_requirements,
    extras_require={
        "mlx": mlx_requirements,
        "audio": optional_audio,
        "all": mlx_requirements + optional_audio,
    },
    entry_points={
        "console_scripts": [
            # Do NOT register as `hermes` — collides with Nous Hermes Agent CLI.
            "unclecode-hermes=hermes.cli:main",
            "uhermes=hermes.cli:main",
        ],
    },
    author="UncleCode",
    author_email="unclecode@kidocode.com",
    description="A versatile video transcription tool (isolated install as unclecode-hermes)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/unclecode/hermes",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    cmdclass={
        "install": PostInstallCommand,
        "develop": PostDevelopCommand,
    },
)
