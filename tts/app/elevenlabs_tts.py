import websockets
import json
import base64
import os
import logging
import asyncio
import hashlib
from tts_interface import TTSInterface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", '')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', '')
ELEVENLABS_MODEL_ID = os.getenv('ELEVENLABS_MODEL_ID', 'eleven_turbo_v2.5')
ELEVENLABS_VOICE_STABILITY = float(os.getenv('ELEVENLABS_VOICE_STABILITY', '0.9'))
ELEVENLABS_VOICE_SIMILARITY = float(os.getenv('ELEVENLABS_VOICE_SIMILARITY', '0.9'))
TTS_SAMPLE_RATE = os.getenv('TTS_SAMPLE_RATE', '24000')

elevenlabs_endpoint = f"wss://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream-input?output_format=pcm_{TTS_SAMPLE_RATE}"

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_key(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

class ElevenLabsTTS(TTSInterface):
    def __init__(self):
        self._is_open = False
        self.elevenlabs_ws = None

    async def initialize(self):
        self._is_open = True
        logger.info("ElevenLabsTTS initialized.")

    async def synthesize(self, content):
        cache_key = get_cache_key(content)
        cache_path = os.path.join(CACHE_DIR, f"{cache_key}.pcm")

        if os.path.exists(cache_path):
            logger.info("Cache hit, sending cached audio")
            with open(cache_path, "rb") as f:
                while chunk := f.read(4096):
                    yield chunk
            return

        self.elevenlabs_ws = await websockets.connect(elevenlabs_endpoint)
        logger.info("Connected to 11labs websocket")

        try:
            input_message = {
                "model_id": ELEVENLABS_MODEL_ID,
                "voice_settings": {
                    "stability": ELEVENLABS_VOICE_STABILITY,
                    "similarity_boost": ELEVENLABS_VOICE_SIMILARITY
                },
                "xi_api_key": ELEVENLABS_API_KEY,
                "text": content,
                "try_trigger_generation": True,
            }
            await self.elevenlabs_ws.send(json.dumps(input_message))
            logger.info("Sent initial message to 11labs")

            eos_message = {"text": ""}
            await self.elevenlabs_ws.send(json.dumps(eos_message))
            logger.info("Sent EOS message to 11labs")

            with open(cache_path, "wb") as f:
                while True:
                    try:
                        response = await self.elevenlabs_ws.recv()
                        data = json.loads(response)
                        if "audio" in data and data["audio"] is not None:
                            audio_data = base64.b64decode(data["audio"])
                            logger.info(f"Received audio chunk from 11labs of size: {len(audio_data)}")
                            f.write(audio_data)
                            yield audio_data
                        elif "error" in data:
                            logger.error(f"Error from 11labs: {data['error']}")
                            raise Exception(f"ElevenLabs API error: {data['error']}")
                        else:
                            logger.info("No more audio data.")
                            break
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse EOS response as JSON")
                        break
                    except asyncio.CancelledError:
                        logger.info("Synthesis task was cancelled")
                        break
        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection closed")
        except Exception as e:
            logger.exception("An error occurred while receiving data from 11labs")
        finally:
            await self.elevenlabs_ws.close()
            self.elevenlabs_ws = None

    async def close(self):
        self._is_open = False
        if self.elevenlabs_ws:
            await self.elevenlabs_ws.close()
        logger.info("ElevenLabsTTS connection closed.")

    @property
    def is_open(self) -> bool:
        return self._is_open