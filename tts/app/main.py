from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import os
import logging
import asyncio
from elevenlabs_tts import ElevenLabsTTS
from deepgram_tts import DeepgramTTS
from openai_tts import OpenAITTS
from cartesia_tts import CartesiaTTS
import textwrap

# Initialize FastAPI app
app = FastAPI()

# Set default TTS provider from environment variable
TTS_PROVIDER = os.environ.get("TTS_PROVIDER", "elevenlabs")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSFactory:
    """Factory class for creating TTS instances."""
    _instance = None

    @classmethod
    def get_instance(cls, provider: str):
        """
        Get or create a TTS instance based on the specified provider.
        
        Args:
            provider (str): The name of the TTS provider.
        
        Returns:
            TTSInterface: An instance of the specified TTS provider.
        
        Raises:
            ValueError: If an unsupported TTS provider is specified.
        """
        if cls._instance is None:
            if provider == "elevenlabs":
                cls._instance = ElevenLabsTTS()
            elif provider == "deepgram":
                cls._instance = DeepgramTTS()
            elif provider == "openai":
                cls._instance = OpenAITTS()
            elif provider == "cartesia":
                cls._instance = CartesiaTTS()
            else:
                raise ValueError(f"Unsupported TTS provider: {provider}")
        return cls._instance

@app.websocket("/api/v1/ws")
async def websocket_endpoint(tts_ws: WebSocket):
    tts_model = TTSFactory.get_instance(TTS_PROVIDER)
    await tts_ws.accept()
    synthesis_task = None

    try:
        await tts_model.initialize()
        logger.info("WebSocket connection established.")

        while True:
            payload = await tts_ws.receive_json()
            action = payload.get("action")
            content = payload.get("text", "")
            logger.info(f"Received action: {action}")

            if action == "synthesize":
                logger.info(f"Received text to synthesize: {content}")
                if synthesis_task:
                    synthesis_task.cancel()
                
                async def synthesize_and_send():
                    for text_chunk in textwrap.wrap(content, 4000):
                        async for audio_chunk in tts_model.synthesize(text_chunk):
                            await tts_ws.send_bytes(audio_chunk)
                    await tts_ws.send_json({"action": "done"})

                synthesis_task = asyncio.create_task(synthesize_and_send())

            elif action == "cancel":
                logger.info("Received cancel action")
                if synthesis_task:
                    synthesis_task.cancel()
                    synthesis_task = None

    except WebSocketDisconnect:
        logger.info("Client disconnected")
    finally:
        if synthesis_task:
            synthesis_task.cancel()
        await tts_model.close()