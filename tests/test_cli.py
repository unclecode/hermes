import pytest
from unittest.mock import patch
from hermes.cli import parse_args, main

def test_parse_args():
    known_args, extra_args = parse_args(['test_source', '-p', 'groq', '-m', 'test_model', '--response_format', 'json'])
    assert known_args.source == 'test_source'
    assert known_args.provider == 'groq'
    assert known_args.model == 'test_model'
    assert known_args.response_format == 'json'
    assert extra_args == {}

@patch('hermes.cli.transcribe')
def test_main_success(mock_transcribe):
    mock_transcribe.return_value = {'transcription': 'Test transcription'}
    with patch('sys.argv', ['hermes', 'test_source']):
        main()
    mock_transcribe.assert_called_once()

@patch('hermes.cli.transcribe')
def test_main_with_output_file(mock_transcribe, tmp_path):
    mock_transcribe.return_value = {'transcription': 'Test transcription'}
    output_file = tmp_path / "output.txt"
    with patch('sys.argv', ['hermes', 'test_source', '-o', str(output_file)]):
        main()
    assert output_file.read_text() == 'Test transcription'

@patch('hermes.cli.transcribe')
def test_main_error(mock_transcribe, capsys):
    mock_transcribe.side_effect = Exception("Test error")
    with patch('sys.argv', ['hermes', 'test_source']):
        with pytest.raises(SystemExit):
            main()
    captured = capsys.readouterr()
    assert "Error: Test error" in captured.err

@patch('hermes.cli.transcribe')
def test_main_with_llm_processing(mock_transcribe):
    mock_transcribe.return_value = {
        'transcription': 'Test transcription',
        'llm_processed': 'Processed result'
    }
    with patch('sys.argv', ['hermes', 'test_source', '--llm_prompt', 'Summarize']):
        main()
    mock_transcribe.assert_called_once_with(
        source='test_source',
        provider='groq',
        force=False,
        llm_prompt='Summarize',
        model=None,
        response_format='text'
    )