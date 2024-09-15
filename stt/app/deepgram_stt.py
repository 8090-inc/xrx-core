import os
import logging
from deepgram.utils import verboselogs
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
)
from stt_interface import STTInterface

API_KEY = os.getenv('DG_API_KEY', '')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepGramSTT(STTInterface):
    def __init__(self):
        self._is_open = False
        self.is_finals = []
        self.text_handler = None

        
        
    async def initialize(self, text_handler: callable = None):
        logger.info("Initializing Deepgram")
        self.text_handler = text_handler
        # config: DeepgramClientOptions = DeepgramClientOptions(
        #     verbose=verboselogs.DEBUG, options={"keepalive": "true"}
        # )
        # self.model = DeepgramClient(API_KEY, config)
        self.model = DeepgramClient(API_KEY)
        
        self.dg_connection = self.model.listen.asyncwebsocket.v("1")
        
        # Define the event handlers for the connection
        self.dg_connection.on(LiveTranscriptionEvents.Open, self.on_open)
        self.dg_connection.on(LiveTranscriptionEvents.Close, self.on_close)
        self.dg_connection.on(LiveTranscriptionEvents.Transcript, self.on_message)
        self.dg_connection.on(LiveTranscriptionEvents.Metadata, self.on_metadata)
        self.dg_connection.on(LiveTranscriptionEvents.Error, self.on_error)

        # Configure Deepgram options for live transcription
        self.options = LiveOptions(
            model="nova-2",
            language="en-US",
            # Apply smart formatting to the output
            # smart_format=True,
            # Raw audio format details
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            # To get UtteranceEnd, the following must be set:
            # interim_results=True,
            # utterance_end_ms="1000",
            #vad_events=True,
            # Time in milliseconds of silence to wait for before finalizing speech
            #endpointing=300,
        )
        self.addons = {
            # Prevent waiting for additional numbers
            "no_delay": "true"
        }
        if await self.dg_connection.start(self.options, addons=self.addons) is False:
            logger.error("Failed to connect to Deepgram")
            return
        self._is_open = True

    async def transcribe(self, data) -> str:
        if not self._is_open:
            await self.initialize(self.text_handler)
        await self.dg_connection.send(data)
        return ''

    async def on_message(self, dg, result, **kwargs):
        # logger.debug(result)
        sentence = result.channel.alternatives[0].transcript
        if len(sentence) == 0:
            return
        logger.info(f"speaker: {sentence}")
        if result.is_final:
            self.is_finals.append(sentence)
            if result.speech_final:
                utterance = " ".join(self.is_finals)
                logger.info(f"Speech Final: {utterance}")
                self.is_finals = []
                # Send the result to the orchestrator
                await self.text_handler(utterance)

    async def on_metadata(self,dg, metadata, **kwargs):
        logger.info(f"Metadata received: {metadata}")

    async def on_error(self, dg, error, **kwargs):
        logger.error(f"Deepgram error: {error}")
        self._is_open = False

    async def on_open(self, dg, open, **kwargs):
        logger.info("Connection to Deepgram opened.")
        self._is_open = True
            
    async def on_close(self, dg, close, **kwargs):
        logger.info(f"Deepgram connection closed: {close}")
        self._is_open = False

    async def close(self):
        self.dg_connection.finish()
        self._is_open = False
        logger.info("Deepgram connection closed.")

    @property
    def is_open(self) -> bool:
        return self._is_open