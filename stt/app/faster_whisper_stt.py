import os
import logging
from faster_whisper import WhisperModel
from stt_interface import STTInterface
import numpy as np

WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "tiny")
STT_LANGUAGE_CODE = os.environ.get("STT_LANGUAGE_CODE", "en")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FasterWhisperSTT(STTInterface):
    """Speech-to-text using the Faster Whisper model."""
    
    _model = None  # Class-level attribute to store the shared WhisperModel instance

    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls._model = WhisperModel(WHISPER_MODEL, compute_type="float32")
            logger.info(f"Faster Whisper (model: {WHISPER_MODEL}) loaded.")
        return cls._model

    def __init__(self):
        self._is_open = False

    async def initialize(self, text_handler: callable = None):
        self._is_open = True
        # We don't need to do anything with text_handler for this implementation
        logger.info("FasterWhisperSTT initialized.")

    async def transcribe(self, data):
        if not self._is_open:
            await self.initialize()

        logger.info("Received segment of size: %d", len(data))
        result = ""
        
        raw_audio_array = np.frombuffer(data, np.int16).flatten().astype(np.float32) / 32768.0
        
        model = self.get_model()  # Get the shared model instance
        segments, info = model.transcribe(audio=raw_audio_array, language=STT_LANGUAGE_CODE)
        for segment in segments:
            logger.info("[%.2fs -> %.2fs] %s", segment.start, segment.end, segment.text)
            result += segment.text + " "
        
        return result

    async def close(self):
        self._is_open = False
        logger.info("FasterWhisperSTT connection closed.")

    @property
    def is_open(self) -> bool:
        return self._is_open
