from abc import ABC, abstractmethod

class TTSInterface(ABC):
    """Interface for text-to-speech services."""

    @abstractmethod
    async def initialize(self):
        """Initialize the TTS service."""
        pass

    @abstractmethod
    async def synthesize(self, text: str):
        """Synthesize text to audio and yield audio chunks."""
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