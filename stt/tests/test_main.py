import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import os
import sys
import numpy as np

# Add the path to the main.py file
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from main import app, STTFactory, FasterWhisperSTT, GroqSTT, DeepGramSTT

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_websocket_connection():
    client = TestClient(app)
    
    # Create mock audio data
    mock_audio = np.random.rand(16000).astype(np.float32)  # 1 second of random audio at 16kHz
    mock_audio_bytes = (mock_audio * 32768).astype(np.int16).tobytes()
    
    with patch("main.STTFactory.get_instance") as mock_get_instance:
        mock_stt = AsyncMock()
        mock_stt.initialize = AsyncMock()
        mock_stt.transcribe = AsyncMock(return_value="Test transcription")
        mock_stt.close = AsyncMock()
        mock_get_instance.return_value = mock_stt
        
        with client.websocket_connect("/api/v1/ws") as websocket:
            websocket.send_bytes(mock_audio_bytes)
            response = websocket.receive_text()
            assert response == "Test transcription"

    mock_stt.initialize.assert_called_once()
    mock_stt.transcribe.assert_called_once()
    mock_stt.close.assert_called_once()

@pytest.mark.asyncio
async def test_stt_factory():
    # Reset the STTFactory instance before each test
    STTFactory._instance = None

    with patch.dict(os.environ, {"STT_PROVIDER": "faster_whisper"}):
        assert isinstance(STTFactory.get_instance("faster_whisper"), FasterWhisperSTT)

    # Reset again before testing the next provider
    STTFactory._instance = None

    with patch.dict(os.environ, {"STT_PROVIDER": "groq"}):
        assert isinstance(STTFactory.get_instance("groq"), GroqSTT)

    # Reset again
    STTFactory._instance = None

    with patch.dict(os.environ, {"STT_PROVIDER": "deepgram"}):
        assert isinstance(STTFactory.get_instance("deepgram"), DeepGramSTT)

    # Reset one more time to test unsupported provider
    STTFactory._instance = None

    with pytest.raises(ValueError):
        STTFactory.get_instance("unsupported_provider")

@pytest.mark.asyncio
async def test_websocket_transcription():
    client = TestClient(app)
    
    # Create mock audio data
    mock_audio = np.random.rand(16000).astype(np.float32)  # 1 second of random audio at 16kHz
    mock_audio_bytes = (mock_audio * 32768).astype(np.int16).tobytes()
    
    mock_stt = AsyncMock()
    mock_stt.initialize = AsyncMock()
    mock_stt.transcribe = AsyncMock(return_value="Mocked transcription")
    mock_stt.close = AsyncMock()
    
    with patch("main.STTFactory.get_instance", return_value=mock_stt):
        with client.websocket_connect("/api/v1/ws") as websocket:
            websocket.send_bytes(mock_audio_bytes)
            response = websocket.receive_text()
            assert response == "Mocked transcription"
    
    mock_stt.initialize.assert_called_once()
    mock_stt.transcribe.assert_called_once()
    mock_stt.close.assert_called_once()

    # Check that the transcribe method received the correct format
    call_args = mock_stt.transcribe.call_args[0][0]
    assert isinstance(call_args, bytes)
    assert len(call_args) == len(mock_audio_bytes)

@pytest.mark.asyncio
async def test_websocket_disconnect():
    client = TestClient(app)
    
    mock_stt = AsyncMock()
    mock_stt.initialize = AsyncMock()
    mock_stt.close = AsyncMock()
    
    with patch("main.STTFactory.get_instance", return_value=mock_stt):
        with client.websocket_connect("/api/v1/ws") as websocket:
            pass  # WebSocket will be closed when exiting the context manager
    
    mock_stt.initialize.assert_called_once()
    mock_stt.close.assert_called_once()

@pytest.mark.asyncio
async def test_multiple_transcriptions():
    client = TestClient(app)
    
    # Create mock audio data
    mock_audio1 = np.random.rand(16000).astype(np.float32)  # 1 second of random audio at 16kHz
    mock_audio_bytes1 = (mock_audio1 * 32768).astype(np.int16).tobytes()
    mock_audio2 = np.random.rand(16000).astype(np.float32)  # Another 1 second of random audio
    mock_audio_bytes2 = (mock_audio2 * 32768).astype(np.int16).tobytes()
    
    mock_stt = AsyncMock()
    mock_stt.initialize = AsyncMock()
    mock_stt.transcribe = AsyncMock(side_effect=["Transcription 1", "Transcription 2"])
    mock_stt.close = AsyncMock()
    
    with patch("main.STTFactory.get_instance", return_value=mock_stt):
        with client.websocket_connect("/api/v1/ws") as websocket:
            websocket.send_bytes(mock_audio_bytes1)
            response1 = websocket.receive_text()
            assert response1 == "Transcription 1"
            
            websocket.send_bytes(mock_audio_bytes2)
            response2 = websocket.receive_text()
            assert response2 == "Transcription 2"
    
    assert mock_stt.transcribe.call_count == 2
    mock_stt.close.assert_called_once()