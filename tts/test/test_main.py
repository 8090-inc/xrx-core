import pytest
import asyncio
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
from unittest.mock import patch, AsyncMock
import json
import os
import sys
import requests

# Add the directory containing the main.py to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

try:
    from main import app, TTSFactory
    from tts_interface import TTSInterface
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"Current sys.path: {sys.path}")
    raise

# Test main is not working

@pytest.fixture
def test_client():
    return TestClient(app)

class MockTTS(TTSInterface):
    async def initialize(self):
        pass

    async def synthesize(self, content):
        yield b"mock_audio_data"

    async def close(self):
        pass

    @property
    def is_open(self):
        return True

@pytest.mark.asyncio
async def test_tts_factory():
    with patch.dict(os.environ, {"TTS_PROVIDER": "elevenlabs"}):
        tts = TTSFactory.get_instance("elevenlabs")
        assert isinstance(tts, TTSInterface)

    with patch.dict(os.environ, {"TTS_PROVIDER": "deepgram"}):
        tts = TTSFactory.get_instance("deepgram")
        assert isinstance(tts, TTSInterface)

    with patch.dict(os.environ, {"TTS_PROVIDER": "openai"}):
        tts = TTSFactory.get_instance("openai")
        assert isinstance(tts, TTSInterface)

    with patch.dict(os.environ, {"TTS_PROVIDER": "cartesia"}):
        tts = TTSFactory.get_instance("cartesia")
        assert isinstance(tts, TTSInterface)

    with pytest.raises(ValueError):
        TTSFactory.get_instance("unsupported_provider")

@pytest.mark.asyncio
async def test_websocket_connection(test_client):
    with patch("main.TTSFactory.get_instance", return_value=MockTTS()):
        with test_client.websocket_connect("/api/v1/ws") as websocket:
            data = {"action": "synthesize", "text": "Hello, world!"}
            await websocket.send_json(data)
            response = await websocket.receive_bytes()
            assert response == b"mock_audio_data"
            
            done_message = await websocket.receive_json()
            assert done_message == {"action": "done"}

@pytest.mark.asyncio
async def test_websocket_invalid_action(test_client):
    with patch("main.TTSFactory.get_instance", return_value=MockTTS()):
        with test_client.websocket_connect("/api/v1/ws") as websocket:
            data = {"action": "invalid_action", "text": "Hello, world!"}
            await websocket.send_json(data)
            with pytest.raises(WebSocketDisconnect):
                await websocket.receive_bytes()

@pytest.mark.asyncio
async def test_websocket_cancel_synthesis(test_client):
    mock_tts = MockTTS()
    mock_tts.synthesize = AsyncMock(side_effect=asyncio.CancelledError)
    
    with patch("main.TTSFactory.get_instance", return_value=mock_tts):
        with test_client.websocket_connect("/api/v1/ws") as websocket:
            await websocket.send_json({"action": "synthesize", "text": "Hello"})
            await websocket.send_json({"action": "cancel"})
            
            with pytest.raises(WebSocketDisconnect):
                await websocket.receive_bytes()

@pytest.mark.asyncio
async def test_caching_mechanism(test_client):
    mock_tts = MockTTS()
    mock_tts.synthesize = AsyncMock(side_effect=[
        [b"audio_data_1"],  # First call
        [b"audio_data_1"],  # Second call (should be cached)
    ])
    
    with patch("main.TTSFactory.get_instance", return_value=mock_tts):
        with test_client.websocket_connect("/api/v1/ws") as websocket:
            # First synthesis
            await websocket.send_json({"action": "synthesize", "text": "Hello"})
            response1 = await websocket.receive_bytes()
            assert response1 == b"audio_data_1"
            await websocket.receive_json()  # "done" message
            
            # Second synthesis (should use cache)
            await websocket.send_json({"action": "synthesize", "text": "Hello"})
            response2 = await websocket.receive_bytes()
            assert response2 == b"audio_data_1"
            await websocket.receive_json()  # "done" message
    
    assert mock_tts.synthesize.call_count == 1  # Should only be called once due to caching

@pytest.mark.asyncio
async def test_error_handling(test_client):
    mock_tts = MockTTS()
    mock_tts.synthesize = AsyncMock(side_effect=Exception("TTS Error"))
    
    with patch("main.TTSFactory.get_instance", return_value=mock_tts):
        with test_client.websocket_connect("/api/v1/ws") as websocket:
            await websocket.send_json({"action": "synthesize", "text": "Hello"})
            
            with pytest.raises(WebSocketDisconnect):
                await websocket.receive_bytes()

if __name__ == "__main__":
    pytest.main([__file__])