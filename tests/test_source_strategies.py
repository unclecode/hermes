import pytest
from unittest.mock import patch, mock_open
from hermes.strategies.source import SourceStrategy, AutoSourceStrategy

def test_get_strategy():
    strategy = SourceStrategy.get_strategy('auto')
    assert isinstance(strategy, AutoSourceStrategy)

    with pytest.raises(ValueError):
        SourceStrategy.get_strategy('invalid_type')

@patch('hermes.strategies.source.auto.AutoSourceStrategy.is_youtube_url')
@patch('hermes.strategies.source.auto.AutoSourceStrategy.is_web_url')
@patch('hermes.strategies.source.youtube.YouTubeSourceStrategy.get_audio')
@patch('hermes.strategies.source.web.WebSourceStrategy.get_audio')
@patch('hermes.strategies.source.file.FileSourceStrategy.get_audio')
def test_auto_source_strategy(mock_file, mock_web, mock_youtube, mock_is_web, mock_is_youtube):
    strategy = AutoSourceStrategy()

    # Test YouTube URL
    mock_is_youtube.return_value = True
    mock_youtube.return_value = b'youtube audio'
    assert strategy.get_audio('https://www.youtube.com/watch?v=v=PNulbFECY-I') == b'youtube audio'

    # Test Web URL
    mock_is_youtube.return_value = False
    mock_is_web.return_value = True
    mock_web.return_value = b'web audio'
    assert strategy.get_audio('https://example.com/audio.mp3') == b'web audio'

    # Test File
    mock_is_youtube.return_value = False
    mock_is_web.return_value = False
    mock_file.return_value = b'file audio'
    assert strategy.get_audio('path/to/audio.mp3') == b'file audio'

@patch('hermes.strategies.source.auto.AutoSourceStrategy.is_youtube_url')
@patch('hermes.strategies.source.auto.AutoSourceStrategy.is_web_url')
def test_auto_source_strategy_url_detection(mock_is_web, mock_is_youtube):
    strategy = AutoSourceStrategy()

    mock_is_youtube.return_value = True
    assert strategy.is_youtube_url('https://www.youtube.com/watch?v=v=PNulbFECY-I')
    assert strategy.is_youtube_url('https://youtu.be/v=PNulbFECY-I')

    mock_is_youtube.return_value = False
    mock_is_web.return_value = True
    assert strategy.is_web_url('https://example.com/audio.mp3')
    assert strategy.is_web_url('http://example.com/audio.wav')

    mock_is_web.return_value = False
    assert not strategy.is_web_url('file:///path/to/audio.mp3')
    assert not strategy.is_web_url('/path/to/audio.mp3')