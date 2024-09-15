import os
import logging
import hashlib
import json
import base64
import asyncio
import websockets
from tts_interface import TTSInterface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY", '')
CARTESIA_VOICE_ID = os.getenv('CARTESIA_VOICE_ID', 'b7d50908-b17c-442d-ad8d-810c63997ed9')
CARTESIA_MODEL_ID = os.getenv('CARTESIA_MODEL_ID', 'sonic-english')
CARTESIA_VERSION = os.getenv('CARTESIA_VERSION', '2024-06-10')
SAMPLE_RATE = os.getenv("TTS_SAMPLE_RATE", "24000")

cartesia_endpoint = f"wss://api.cartesia.ai/tts/websocket?api_key={CARTESIA_API_KEY}&cartesia_version={CARTESIA_VERSION}"

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_key(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

class CartesiaTTS(TTSInterface):
    def __init__(self):
        self._is_open = False
        self.cartesia_ws = None
        self.context_id = None

    async def initialize(self):
        self._is_open = True
        logger.info("CartesiaTTS initialized.")

    async def synthesize(self, content):
        cache_key = get_cache_key(content)
        cache_path = os.path.join(CACHE_DIR, f"{cache_key}.pcm")

        if os.path.exists(cache_path):
            logger.info("Cache hit, sending cached audio")
            with open(cache_path, "rb") as f:
                while chunk := f.read(4096):
                    yield chunk
            return

        self.cartesia_ws = await websockets.connect(cartesia_endpoint)
        logger.info("Connected to Cartesia websocket")

        try:
            self.context_id = os.urandom(16).hex()
            input_message = {
                "transcript": content,
                "continue": True,
                "context_id": self.context_id,
                "model_id": CARTESIA_MODEL_ID,
                "voice": {
                    "mode": "id",
                    "id": CARTESIA_VOICE_ID
                },
                "output_format": {
                    "container": "raw",
                    "encoding": "pcm_s16le",
                    "sample_rate": SAMPLE_RATE,
                },
                "language": "en",
                #"add_timestamps": True,
            }
            await self.cartesia_ws.send(json.dumps(input_message))
            logger.info(f"Sent initial message to Cartesia: {input_message}")

            with open(cache_path, "wb") as f:
                async for message in self.cartesia_ws:
                    msg = json.loads(message)
                    if msg["context_id"] != self.context_id:
                        logger.warning(f"Received message with mismatched context_id: {msg['context_id']}")
                        continue
                    if msg["type"] == "done":
                        logger.info("Synthesis completed")
                        break
                    elif msg["type"] == "chunk":
                        audio_data = base64.b64decode(msg["data"])
                        logger.info(f"Received audio chunk from Cartesia of size: {len(audio_data)} bytes")
                        f.write(audio_data)
                        yield audio_data
                    elif msg["type"] == "timestamps":
                        logger.debug(f"Received timestamps: {msg['word_timestamps']}")
                    else:
                        logger.warning(f"Received unexpected message type: {msg['type']}")

        except websockets.exceptions.ConnectionClosed:
            logger.error("Cartesia websocket connection closed unexpectedly")
        except json.JSONDecodeError:
            logger.error("Failed to parse response as JSON")
        except asyncio.CancelledError:
            logger.info("Synthesis task was cancelled")
        except Exception as e:
            logger.exception(f"An error occurred while receiving data from Cartesia: {str(e)}")
        finally:
            await self.cartesia_ws.close()
            self.cartesia_ws = None
            self.context_id = None

    async def close(self):
        self._is_open = False
        if self.cartesia_ws:
            await self.cartesia_ws.close()
        logger.info("CartesiaTTS connection closed.")

    @property
    def is_open(self) -> bool:
        return self._is_open