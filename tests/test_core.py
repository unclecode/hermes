import os, sys
# Append the parent directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from unittest.mock import Mock, patch, ANY
from hermes.core import Hermes, transcribe

@pytest.fixture
def mock_hermes():
    with patch('hermes.core.SourceStrategy'), \
         patch('hermes.core.ProviderStrategy'), \
         patch('hermes.core.Cache'), \
         patch('hermes.core.LLMProcessor'):
        yield Hermes()

def test_hermes_initialization(mock_hermes):
    assert mock_hermes.source_strategy is not None
    assert mock_hermes.provider_strategy is not None
    assert mock_hermes.cache is not None
    assert mock_hermes.llm_processor is not None

def test_hermes_transcribe(mock_hermes):
    mock_hermes.cache.get.return_value = None
    mock_hermes.source_strategy.get_audio.return_value = b'audio_data'
    mock_hermes.provider_strategy.transcribe.return_value = 'Transcription result'
    
    result = mock_hermes.transcribe('test_source')
    
    assert result['source'] == 'test_source'
    assert result['transcription'] == 'Transcription result'
    mock_hermes.source_strategy.get_audio.assert_called_once_with('test_source')
    mock_hermes.provider_strategy.transcribe.assert_called_once_with(
        b'audio_data',
        params={'provider': ANY, 'model': ANY}
    )
    mock_hermes.cache.set.assert_called_once()

def test_hermes_transcribe_cached(mock_hermes):
    mock_hermes.cache.get.return_value = {'cached': 'result'}
    
    result = mock_hermes.transcribe('test_source')
    
    assert result == {'cached': 'result'}
    mock_hermes.source_strategy.get_audio.assert_not_called()
    mock_hermes.provider_strategy.transcribe.assert_not_called()

@patch('hermes.core.Hermes')
def test_transcribe_function(mock_hermes_class):
    mock_hermes_instance = Mock()
    mock_hermes_class.from_config.return_value = mock_hermes_instance
    mock_hermes_instance.transcribe.return_value = {'transcription': 'Test'}
    
    result = transcribe('test_source', provider='test_provider', force=True)
    
    assert result['transcription'] == 'Test'
    mock_hermes_class.from_config.assert_called_once()
    mock_hermes_instance.transcribe.assert_called_once_with('test_source', force=True, response_format='text')

def test_hermes_process_with_llm(mock_hermes):
    mock_hermes.llm_processor.process.return_value = 'Processed result'
    
    result = mock_hermes.process_with_llm('Test transcription', 'Summarize')
    
    assert result == 'Processed result'
    mock_hermes.llm_processor.process.assert_called_once_with('Test transcription', 'Summarize')
    
if __name__ == "__main__":
    pytest.main()