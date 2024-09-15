from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import os
import logging
from groq_stt import GroqSTT
from deepgram_stt import DeepGramSTT
from faster_whisper_stt import FasterWhisperSTT

app = FastAPI()
STT_PROVIDER = os.environ.get("STT_PROVIDER", "faster_whisper")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class STTFactory:
    _instance = None

    @classmethod
    def get_instance(cls, provider: str):
        if cls._instance is None:
            if provider == "faster_whisper":
                cls._instance = FasterWhisperSTT()
            elif provider == "groq":
                cls._instance = GroqSTT()
            elif provider == "deepgram":
                cls._instance = DeepGramSTT()
            else:
                raise ValueError(f"Unsupported STT provider: {provider}")
        return cls._instance

@app.websocket("/api/v1/ws")
async def websocket_endpoint(websocket: WebSocket):
    stt_model = STTFactory.get_instance(STT_PROVIDER)
    await websocket.accept()
    try:
        logger.info("WebSocket connection established.")

        async def text_handler(text):
            await websocket.send_text(text)

        await stt_model.initialize(text_handler)

        while True:
            data = await websocket.receive_bytes()
            result = await stt_model.transcribe(data)

            if result:
                await websocket.send_text(result)
                
    except WebSocketDisconnect:
        await stt_model.close()
        logger.info("Client disconnected")
