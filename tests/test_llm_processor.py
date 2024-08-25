import pytest
from unittest.mock import patch, Mock
from hermes.utils.llm import LLMProcessor

@pytest.fixture
def mock_config():
    return {
        'llm': {
            'provider': 'groq',
            'model': 'llama-3.1-8b-instant',
            'api_key': 'test_api_key'
        }
    }

def test_llm_processor_initialization(mock_config):
    with patch('hermes.utils.llm.CONFIG', mock_config):
        processor = LLMProcessor()
        assert processor.config == mock_config['llm']

def test_llm_processor_missing_api_key():
    with patch('hermes.utils.llm.CONFIG', {'llm': {'provider': 'openai', 'model': 'gpt-3.5-turbo', 'api_key': None}}):
        with pytest.raises(ValueError, match="API key for openai is required"):
            LLMProcessor()

@patch('hermes.utils.llm.completion')
def test_llm_processor_process(mock_completion, mock_config):
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='Processed result'))]
    mock_completion.return_value = mock_response

    with patch('hermes.utils.llm.CONFIG', mock_config):
        processor = LLMProcessor()
        result = processor.process('Test input', 'Test prompt')

    assert result == 'Processed result'
    mock_completion.assert_called_once_with(
        model=mock_config['llm']['model'],
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Test prompt\n\nText: Test input"}
        ],
        api_key='test_api_key'
    )