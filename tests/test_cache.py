import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from hermes.utils.cache import Cache

@pytest.fixture
def cache():
    return Cache({'enabled': True, 'directory': '/tmp/hermes_cache'})

def test_cache_initialization(cache):
    assert cache.enabled == True
    assert cache.cache_dir == Path('/tmp/hermes_cache')

@patch('pathlib.Path.mkdir')
def test_cache_directory_creation(mock_mkdir):
    Cache({'enabled': True, 'directory': '/tmp/hermes_cache'})
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

@patch('pathlib.Path.exists')
@patch('builtins.open', new_callable=mock_open, read_data='{"transcription": "test_value"}')
def test_cache_get(mock_file, mock_exists, cache):
    mock_exists.return_value = True
    
    result = cache.get('test_key')
    
    assert result == 'test_value'
    mock_file.assert_called_once_with(Path('/tmp/hermes_cache/test_key.json'), 'r')

def test_cache_get_disabled():
    disabled_cache = Cache({'enabled': False})
    result = disabled_cache.get('test_key')
    assert result is None

@patch('pathlib.Path.exists')
def test_cache_get_nonexistent(mock_exists, cache):
    mock_exists.return_value = False
    result = cache.get('nonexistent_key')
    assert result is None

@patch('builtins.open', new_callable=mock_open)
@patch('json.dump')
def test_cache_set(mock_json_dump, mock_file, cache):
    cache.set('test_key', 'test_value')
    mock_file.assert_called_once_with(Path('/tmp/hermes_cache/test_key.json'), 'w')
    mock_json_dump.assert_called_once_with({'transcription': 'test_value'}, mock_file())

def test_cache_set_disabled():
    disabled_cache = Cache({'enabled': False})
    disabled_cache.set('test_key', 'test_value')
    # No assertion needed, just make sure it doesn't raise an exception

@patch('pathlib.Path.exists')
@patch('builtins.open', new_callable=mock_open, read_data='{"transcription": "old_value"}')
@patch('json.dump')
def test_cache_update(mock_json_dump, mock_file, mock_exists, cache):
    mock_exists.return_value = True
    cache.set('test_key', 'new_value')
    mock_file.assert_any_call(Path('/tmp/hermes_cache/test_key.json'), 'w')
    mock_json_dump.assert_called_once_with({'transcription': 'new_value'}, mock_file())

@patch('pathlib.Path.exists')
@patch('pathlib.Path.unlink')
def test_cache_clear(mock_unlink, mock_exists, cache):
    mock_exists.return_value = True
    cache.clear()

def test_cache_clear_disabled():
    disabled_cache = Cache({'enabled': False})
    disabled_cache.clear()
    # No assertion needed, just make sure it doesn't raise an exception