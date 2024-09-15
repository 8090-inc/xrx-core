
from abc import ABC, abstractmethod

class STTInterface(ABC):
    """Interface for speech-to-text services."""

    @abstractmethod
    async def initialize(self, text_handler: callable = None):
        """Initialize the STT service."""
        pass

    @abstractmethod
    async def transcribe(self, data: bytearray) -> str:
        """Transcribe audio data to text."""
        pass

    @abstractmethod
    async def close(self):
        """Close the connection to the service."""
        pass

    @property
    @abstractmethod
    def is_open(self) -> bool:
        """Check if the connection is open."""
        pass