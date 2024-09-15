import os
import logging
import hashlib
from tts_interface import TTSInterface
from openai import OpenAI
import io
import numpy as np
import resampy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", '')
OPENAI_TTS_MODEL = os.environ.get('OPENAI_TTS_MODEL', 'tts-1')
OPENAI_TTS_VOICE = os.environ.get('OPENAI_TTS_VOICE', 'alloy')
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Openai TTS has a sample rate of 24kHz.
# xRx works at 16kHz. To avoid glitches in resampling the audio, the chunk size has been increased to 12288 from the original 4096 bytes.
# Latency will be affected.

CHUNK_SIZE = 12288

def get_cache_key(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

class OpenAITTS(TTSInterface):
    def __init__(self):
        self._is_open = False
        self.client = None

    async def initialize(self):
        self._is_open = True
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAITTS initialized.")

    async def synthesize(self, content):
        cache_key = get_cache_key(content)
        cache_path = os.path.join(CACHE_DIR, f"{cache_key}.pcm")

        if os.path.exists(cache_path):
            logger.info("Cache hit, sending cached audio")
            with open(cache_path, "rb") as f:
                while chunk := f.read(CHUNK_SIZE):
                    yield chunk
            yield b''  # Signal end of stream
            return

        try:
            logger.info(f"Synthesizing speech for content: {content[:50]}...")
            response = self.client.audio.speech.create(
                model=OPENAI_TTS_MODEL,
                voice=OPENAI_TTS_VOICE,
                input=content,
                response_format="pcm"
            )

            buffer = b""
            cache_buffer = io.BytesIO()
            chunk_count = 0

            for chunk in response.iter_bytes(chunk_size=CHUNK_SIZE):
                buffer += chunk
                while len(buffer) >= CHUNK_SIZE:
                    audio_data = np.frombuffer(buffer[:CHUNK_SIZE], dtype=np.int16)
                    resampled_chunk = resampy.resample(audio_data, 24000, 16000)
                    resampled_bytes = resampled_chunk.astype(np.int16).tobytes()
                    
                    cache_buffer.write(resampled_bytes)
                    yield resampled_bytes
                    
                    buffer = buffer[CHUNK_SIZE:]
                    chunk_count += 1
                    logger.debug(f"Processed chunk {chunk_count}, size: {len(resampled_bytes)} bytes")
            
            # Process any remaining audio data
            if buffer:
                audio_data = np.frombuffer(buffer, dtype=np.int16)
                resampled_chunk = resampy.resample(audio_data, 24000, 16000)
                resampled_bytes = resampled_chunk.astype(np.int16).tobytes()
                cache_buffer.write(resampled_bytes)
                yield resampled_bytes
                chunk_count += 1
                logger.debug(f"Processed final chunk {chunk_count}, size: {len(resampled_bytes)} bytes")

            # Write the entire resampled audio to cache
            with open(cache_path, "wb") as f:
                f.write(cache_buffer.getvalue())
            logger.info(f"Cached synthesized audio to {cache_path}")

            logger.info(f"Finished synthesizing speech. Total chunks: {chunk_count}")
            yield b''  # Signal end of stream

        except Exception as e:
            logger.exception(f"An error occurred while synthesizing speech: {str(e)}")
            yield b''  # Signal end of stream even in case of error
            raise

    async def close(self):
        self._is_open = False
        self.client = None
        logger.info("OpenAITTS connection closed.")

    @property
    def is_open(self) -> bool:
        return self._is_open