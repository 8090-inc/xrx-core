import io
import os
import json
import logging
from groq import Groq
from stt_interface import STTInterface

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STT_LANGUAGE_CODE = os.getenv('STT_LANGUAGE_CODE', 'en')
NO_SPEECH_THRESHOLD = float(os.getenv('NO_SPEECH_THRESHOLD', '0.7'))
API_KEY = os.environ.get('GROQ_STT_API_KEY', '')

class GroqSTT(STTInterface):
    _model = None  # Class-level attribute to store the shared Groq instance

    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls._model = Groq(api_key=API_KEY)
            logger.info("Groq model initialized.")
        return cls._model

    def __init__(self):
        self._is_open = False

    async def initialize(self, text_handler: callable = None):
        self._is_open = True
        logger.info("GroqSTT initialized.")

    def generate_wav_header(self, num_channels, num_samples, sample_rate, bits_per_sample)->bytearray:
        # Generate the WAV header
        byte_rate = sample_rate * num_channels * bits_per_sample // 8
        block_align = num_channels * bits_per_sample // 8

        header = bytearray()
        header.extend(b'RIFF')
        header.extend((num_samples + 36).to_bytes(4, 'little'))
        header.extend(b'WAVE')
        header.extend(b'fmt ')
        header.extend((16).to_bytes(4, 'little'))
        header.extend((1).to_bytes(2, 'little'))
        header.extend(num_channels.to_bytes(2, 'little'))
        header.extend(sample_rate.to_bytes(4, 'little'))
        header.extend(byte_rate.to_bytes(4, 'little'))
        header.extend(block_align.to_bytes(2, 'little'))
        header.extend(bits_per_sample.to_bytes(2, 'little'))
        header.extend(b'data')
        header.extend(num_samples.to_bytes(4, 'little'))

        return header

    async def transcribe(self, data)->str:
        if not self._is_open:
            await self.initialize()
        
        logger.info("Transcribing audio using Groq API...")
        header = self.generate_wav_header(
            num_channels=1,
            num_samples=len(data),
            sample_rate=16000,
            bits_per_sample=16
        )

        # Combine the header and raw_audio_array
        audio_data = header + data
        stream = io.BytesIO(audio_data)

        model = self.get_model()  # Get the shared model instance
        transcription = model.audio.transcriptions.create(
            file=('audio.wav', stream.read()),
            model="whisper-large-v3",
            response_format="verbose_json",
            temperature=0.0,
            language=STT_LANGUAGE_CODE
        )
        logger.info('-----')
        logger.info(transcription) 

        if len(transcription.segments) == 0:
            logger.info(f'no segments in transcription indicating no speech')
            return ''

        if transcription.segments[0]['no_speech_prob'] > NO_SPEECH_THRESHOLD:
            no_speech_prob = transcription.segments[0]['no_speech_prob']
            logger.info(f'no_speech_prob {no_speech_prob} exceeds threshold of {NO_SPEECH_THRESHOLD}')
            return ''
        
        return transcription.text
    
    async def close(self):
        self._is_open = False
        logger.info("GroqSTT connection closed.")

    @property
    def is_open(self) -> bool:
        return self._is_open
