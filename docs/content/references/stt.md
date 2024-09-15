---
sidebar_position: 2
---

# Speech-To-Text (STT)

### Overview
This WebSocket API allows clients to connect to a server for real-time speech-to-text (STT) transcription. The server supports multiple STT providers and handles both text and binary messages.

### Endpoint
- **URL:** `/api/v1/ws`
- **Method:** `GET`
- **Protocol:** WebSocket

### Environment Variables
- [STT_PROVIDER](https://github.com/8090-inc/xrx/blob/main/orchestrator/src/Session.ts#30%2C7-30%2C7): Specifies the STT provider to use (`"faster_whisper"`, `"groq"`, `"deepgram"`). Default is `"faster_whisper"`.

### Connection
Upon connecting to the WebSocket endpoint, the server will log the connection and initialize the STT model.

### Messages
The server handles binary messages containing audio data.

#### Binary Messages
- **Format:** Binary audio data. All STT providers are expecting PCM, 16-bit, 16000 Hz, mono audio.

### Events

#### [message](https://github.com/8090-inc/xrx/blob/main/orchestrator/src/Session.ts#133%2C75-133%2C75)
- **Description:** Triggered when a binary message (audio data) is received from the client.
- **Parameters:**
  - [data](https://github.com/8090-inc/xrx/blob/main/orchestrator/src/Session.ts#178%2C59-178%2C59): The binary message data (audio)

**Handling Binary Messages:**
- The server will transcribe the binary data (audio) to text using the configured STT model and send the transcribed text back to the client.

#### [close](https://github.com/8090-inc/xrx/blob/main/orchestrator/src/Session.ts#172%2C5-172%2C5)
- **Description:** Triggered when the client closes the connection.
- **Parameters:**
  - [code](https://github.com/8090-inc/xrx/blob/main/orchestrator/src/Index.ts#38%2C21-38%2C21): The close code
  - [reason](https://github.com/8090-inc/xrx/blob/main/orchestrator/src/Index.ts#93%2C35-93%2C35): The reason for closing

### Server Responses

#### Text Responses
- **Format:** Plain text
- **Content:** The transcribed text from the audio data

### Error Handling
- If the STT provider is unsupported, the server raises a [ValueError](https://github.com/8090-inc/xrx/blob/main/stt/app/main.py#28%2C23-28%2C23).
- If the WebSocket connection is disconnected, the server logs the disconnection and closes the STT model.

### Example Usage

**Connecting to the WebSocket:**
```javascript
const socket = new WebSocket('ws://localhost:8000/api/v1/ws');

socket.onopen = () => {
  console.log('Connection opened');
};

socket.onmessage = (event) => {
  console.log('Received message:', event.data);
};

socket.onclose = (event) => {
  console.log(`Connection closed: ${event.code} ${event.reason}`);
};

socket.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

**Sending a Binary Message:**
```javascript
const audioData = new Uint8Array([/* audio data */]);
socket.send(audioData);
```

### FastAPI Application Code

```python
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
```

### STT Interface Code

```python
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
```

This documentation provides an overview of the WebSocket API, including connection details, message formats, events, and example usage for the STT service.