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
    'commentary': {
        'provider': 'openai',
        'model': 'gpt-4o-mini',
        'api_key': None,
    },
    'tts': {
        'provider': 'openai',
        'api_key': None,
        'voice_id': 'alloy',
    },
    # 'tts': {
    #     'provider': 'elevenlabs',
    #     'api_key': None,
    #     'voice_id': 'UDoSXdwuEuC59qu2AfUo',
    # },
    'background_music': {
        'default_path': None,
        'volume': 0.2,
        'fade_duration': 3,
    },
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
    for service in ['llm', 'transcription', 'commentary', 'tts']:
        provider = config[service]['provider']
        env_var = f"{provider.upper()}_API_KEY"

        # If API key is not in config, try to get it from environment
        if not config[service]['api_key']:
            config[service]['api_key'] = os.getenv(env_var)

        # If still no API key, raise an error
        if not config[service]['api_key']:
            print(f"No API key found for {provider}. To use {service} with {provider}, set the key in the config file or as environment variable {env_var}. If you don't intend to use this provider, you can ignore this message.")

    # Expand user directory for cache
    config['cache']['directory'] = os.path.expanduser(config['cache']['directory'])

    return config

CONFIG = load_config()