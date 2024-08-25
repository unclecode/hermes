import os, sys
# Add the parent directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from hermes.core import transcribe

@pytest.mark.integration
def test_transcribe_local_file():
    result = transcribe('tests/assets/input.mp4', provider='groq')
    assert 'transcription' in result
    assert isinstance(result['transcription'], str)
    assert len(result['transcription']) > 0

@pytest.mark.integration
def test_transcribe_youtube_video():
    result = transcribe('https://www.youtube.com/watch?v=v=PNulbFECY-I', provider='openai')
    assert 'transcription' in result
    assert isinstance(result['transcription'], str)
    assert len(result['transcription']) > 0

@pytest.mark.integration
def test_transcribe_with_llm_processing():
    result = transcribe('tests/assets/input.mp4', provider='groq', llm_prompt='Summarize this transcription')
    assert 'transcription' in result
    assert 'llm_processed' in result
    assert isinstance(result['llm_processed'], str)
    assert len(result['llm_processed']) > 0

@pytest.mark.integration
def test_transcribe_with_different_response_formats():
    for format in ['json', 'text', 'srt', 'vtt']:
        result = transcribe('tests/assets/input.mp4', provider='mlx', response_format=format)
        assert 'transcription' in result
        if format == 'json':
            assert isinstance(result['transcription'], dict)
        else:
            assert isinstance(result['transcription'], str)
            
if __name__ == "__main__":
    pytest.main(["-v", __file__])