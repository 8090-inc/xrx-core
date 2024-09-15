import os
import logging
import hashlib
from tts_interface import TTSInterface
import requests
from requests.exceptions import RequestException
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DG_API_KEY = os.getenv("DG_API_KEY", '')
DG_TTS_MODEL_VOICE = os.environ.get('DG_TTS_MODEL_VOICE', 'aura-asteria-en')
SAMPLE_RATE = os.getenv("TTS_SAMPLE_RATE", "24000")

encoding = "linear16"  # PCM 16000
sample_rate = SAMPLE_RATE

DEEPGRAM_URL = f"https://api.deepgram.com/v1/speak?model={DG_TTS_MODEL_VOICE}&encoding={encoding}&sample_rate={sample_rate}&container=none"

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def get_cache_key(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

class DeepgramTTS(TTSInterface):
    def __init__(self):
        self._is_open = False

    async def initialize(self):
        self._is_open = True
        logger.info("DeepgramTTS initialized.")

    async def synthesize(self, content):
        cache_key = get_cache_key(content)
        cache_path = os.path.join(CACHE_DIR, f"{cache_key}.pcm")

        if os.path.exists(cache_path):
            logger.info("Cache hit, sending cached audio")
            with open(cache_path, "rb") as f:
                while chunk := f.read(4096):
                    yield chunk
            return

        headers = {
            "Authorization": f"Token {DG_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "text": content
        }

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(DEEPGRAM_URL, headers=headers, json=payload, stream=True)
            )
            response.raise_for_status()
            logger.info("Sent initial message to Deepgram")

            with open(cache_path, "wb") as f:
                async for chunk in self._iter_content(response):
                    if chunk:
                        logger.info(f"Received audio chunk from Deepgram of size: {len(chunk)}")
                        await loop.run_in_executor(None, f.write, chunk)
                        yield chunk
            logger.info("No more audio data.")

        except RequestException as e:
            logger.error(f"Error from Deepgram: {str(e)}")
            raise Exception(f"Deepgram API error: {str(e)}")
        except asyncio.CancelledError:
            logger.info("Synthesis task was cancelled")
        except Exception as e:
            logger.exception("An error occurred while receiving data from Deepgram")

    async def _iter_content(self, response):
        loop = asyncio.get_event_loop()
        while True:
            chunk = await loop.run_in_executor(None, response.raw.read, 4096)
            if not chunk:
                break
            yield chunk

    async def close(self):
        self._is_open = False
        logger.info("DeepgramTTS connection closed.")

    @property
    def is_open(self) -> bool:
        return self._is_open