from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import sys
import yaml
from pathlib import Path

# Read requirements.txt
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# Remove MLX-specific requirements for the MLX-free version
requirements_without_mlx = [req for req in requirements if not req.startswith('mlx-')]

# Define the default configuration
DEFAULT_CONFIG = {
    'llm': {
        'provider': 'groq',
        'model': 'llama-3.1-8b-instant',
        'api_key': None,
    },
    'transcription': {
        'provider': 'groq',
        'model': 'distil-whisper-large-v3-en',
    },
    'cache': {
        'enabled': True,
        'directory': '~/.hermes/cache',
    },
    'source_type': 'auto',
}

def post_install():
    # Create ~/.hermes directory
    hermes_dir = Path.home() / '.hermes'
    hermes_dir.mkdir(parents=True, exist_ok=True)

    # Create config.yaml if it doesn't exist
    config_path = hermes_dir / 'config.yaml'
    if not config_path.exists():
        with open(config_path, 'w') as f:
            yaml.dump(DEFAULT_CONFIG, f)

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        post_install()

# Determine if we're installing the MLX-free version
is_mlx_free = '--without-mlx' in sys.argv
if is_mlx_free:
    sys.argv.remove('--without-mlx')
    install_requires = requirements_without_mlx
else:
    install_requires = requirements

setup(
    name="hermes",
    version="0.1.0",
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "hermes=hermes.cli:main",
        ],
    },
    author="UncleCode",
    author_email="unclecode@kidocode.com",
    description="A versatile video transcription tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/unclecode/hermes",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    cmdclass={
        'install': PostInstallCommand,
    },
)