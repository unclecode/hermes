import pytest
from unittest.mock import patch, Mock
from hermes.strategies.provider import ProviderStrategy, GroqProviderStrategy, OpenAIProviderStrategy, MLXProviderStrategy


def test_get_strategy():
    groq_strategy = ProviderStrategy.get_strategy('groq')
    assert isinstance(groq_strategy, GroqProviderStrategy)

    openai_strategy = ProviderStrategy.get_strategy('openai')
    assert isinstance(openai_strategy, OpenAIProviderStrategy)

    mlx_strategy = ProviderStrategy.get_strategy('mlx')
    assert isinstance(mlx_strategy, MLXProviderStrategy)

    with pytest.raises(ValueError):
        ProviderStrategy.get_strategy('invalid_provider')

@patch('os.getenv')
@patch('requests.post')
def test_groq_provider_strategy(mock_post, mock_getenv):
    mock_getenv.return_value = 'fake_api_key'
    mock_response = Mock()
    mock_response.text = 'Transcription result'
    mock_post.return_value = mock_response

    strategy = GroqProviderStrategy()
    result = strategy.transcribe(b'audio data', {'model': 'test-model', 'response_format': 'text'})

    assert result == 'Transcription result'
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == 'https://api.groq.com/openai/v1/audio/transcriptions'
    assert kwargs['headers']['Authorization'] == 'Bearer fake_api_key'
    assert kwargs['data']['model'] == 'test-model'
    assert kwargs['data']['response_format'] == 'text'

@patch('os.getenv')
@patch('openai.Audio.transcribe')
def test_openai_provider_strategy(mock_transcribe, mock_getenv):
    mock_getenv.return_value = 'fake_api_key'
    mock_transcribe.return_value.text = 'OpenAI transcription result'

    strategy = OpenAIProviderStrategy()
    result = strategy.transcribe(b'audio data', {'model': 'whisper-1', 'response_format': 'text'})

    assert result == 'OpenAI transcription result'
    mock_transcribe.assert_called_once_with(
        model='whisper-1',
        file=('audio.wav', b'audio data'),
        response_format='text'
    )

@patch('subprocess.run')
def test_mlx_provider_strategy(mock_run):
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = 'MLX transcription result'

    with patch('builtins.open', mock_open(read_data='MLX transcription result')):
        strategy = MLXProviderStrategy()
        result = strategy.transcribe(b'audio data', {'model': 'mlx-community/test-model'})

    assert result == 'MLX transcription result'
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[0][0] == 'mlx_whisper'
    assert args[0][2] == '--model'
    assert args[0][3] == 'mlx-community/test-model'