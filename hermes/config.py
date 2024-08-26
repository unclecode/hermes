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
        'api_key': None,
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

    # Handle API keys
    for service in ['llm', 'transcription']:
        provider = config[service]['provider']
        env_var = f"{provider.upper()}_API_KEY"
        
        # If API key is not in config, try to get it from environment
        if not config[service]['api_key']:
            config[service]['api_key'] = os.getenv(env_var)
        
        # If still no API key, raise an error
        if not config[service]['api_key']:
            raise ValueError(f"No API key found for {provider} in config or environment variable {env_var}. "
                             f"Please set it in your config file or as an environment variable.")

    # Expand user directory for cache
    config['cache']['directory'] = os.path.expanduser(config['cache']['directory'])

    return config

CONFIG = load_config()