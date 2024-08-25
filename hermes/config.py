import os
import yaml
from typing import Dict, Any

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

def load_config() -> Dict[str, Any]:
    config_path = os.path.expanduser('~/.hermes/config.yml')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            user_config = yaml.safe_load(f)
    else:
        user_config = {}

    # Merge user config with default config
    config = {**DEFAULT_CONFIG, **user_config}

    # Set API keys from environment variables if not in config
    for provider in ['groq', 'openai']:
        env_var = f"{provider.upper()}_API_KEY"
        if config['llm']['provider'] == provider and not config['llm'].get('api_key'):
            config['llm']['api_key'] = os.getenv(env_var)

    # Expand user directory for cache
    config['cache']['directory'] = os.path.expanduser(config['cache']['directory'])

    return config

CONFIG = load_config()