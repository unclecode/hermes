import pytest
from unittest.mock import patch, mock_open
from hermes.config import load_config, DEFAULT_CONFIG
import os

@pytest.fixture
def mock_config_file():
    config_content = """
    llm:
      provider: test_provider
      model: test_model
      api_key: test_key
    transcription:
      provider: test_transcription_provider
    """
    return mock_open(read_data=config_content)

def test_load_config_default():
    with patch('os.path.exists', return_value=False):
        config = load_config()
    assert config == DEFAULT_CONFIG

def test_load_config_custom(mock_config_file):
    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', mock_config_file):
        config = load_config()
    assert config['llm']['provider'] == 'test_provider'
    assert config['llm']['model'] == 'test_model'
    assert config['transcription']['provider'] == 'test_transcription_provider'

def test_load_config_env_vars():
    with patch('os.path.exists', return_value=False), \
        patch.dict('os.environ', {'GROQ_API_KEY': 'test_key'}, clear=True):
        config = load_config()
    assert config['llm']['api_key'] == os.environ['GROQ_API_KEY']

# Add more tests as needed