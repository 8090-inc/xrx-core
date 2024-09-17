---
sidebar_position: 3
---

# Text-To-Speech (TTS)

## Overview
The Text-to-Speech (TTS) module is a FastAPI service that provides real-time synthesis of text to speech using multiple TTS providers. This module establishes a WebSocket connection to receive text input and returns synthesized speech in binary format.

### Endpoint
- **URL:** `/api/v1/ws`
- **Method:** `GET`
- **Protocol:** WebSocket

### Authentication
- **Header:** None required for the WebSocket connection itself.
- **Environment Variables:** 
  - `TTS_PROVIDER`: Specifies the TTS provider to use (default: "elevenlabs")
  - Provider-specific API keys and settings (see [Environment Variables](#environment-variables) section)

### Connection
Upon connecting to the WebSocket endpoint, the server initializes the specified TTS provider and prepares to handle incoming messages.

### Messages
The server handles JSON messages to initiate or cancel the text-to-speech synthesis process.

#### JSON Messages
- **Format:** JSON
- **Fields:**
  - `action`: `"synthesize"` or `"cancel"`
  - `text`: The text content to be synthesized (required if `action` is `"synthesize"`)

**Example:**
```json
{
  "action": "synthesize",
  "text": "Hello, how can I assist you today?"
}
```

### Events

#### `message`
- **Description:** Triggered when a message is received from the client.
- **Parameters:**
  - `message`: The message data (JSON)
  
**Handling Synthesize Messages:**
- If `action` is `"synthesize"`, the server will begin the synthesis process and stream the resulting audio data back to the client.

**Handling Cancel Messages:**
- If `action` is `"cancel"`, the server will cancel any ongoing synthesis tasks.

#### `close`
- **Description:** Triggered when the client closes the connection.

### Server Responses

#### Binary Responses
- **Format:** Binary data (audio data)
- **Description:** The synthesized speech audio data is sent in chunks as it is received from the TTS provider.

#### JSON Responses
- **Format:** JSON
- **Fields:**
  - `action`: Indicates completion with `"done"`

**Example:**
```json
{
  "action": "done"
}
```

### Error Handling
- If the TTS provider connection fails or an error occurs during synthesis, the server logs the error and closes the WebSocket connection.
- The server caches synthesized audio to avoid redundant processing for identical text inputs.

### Environment Variables
- `TTS_PROVIDER`: Specifies the TTS provider to use (default: "elevenlabs")
- `TTS_SAMPLE_RATE`: Specifies the sample rate for the TTS output (default: 24000Hz)
- ElevenLabs:
  - `ELEVENLABS_API_KEY`: API key for ElevenLabs authentication
  - `ELEVENLABS_VOICE_ID`: Voice ID for the ElevenLabs TTS service
  - `ELEVENLABS_MODEL_ID`: Model ID for ElevenLabs (default: "eleven_turbo_v2.5")
  - `ELEVENLABS_VOICE_STABILITY`: Voice stability setting (default: 0.9)
  - `ELEVENLABS_VOICE_SIMILARITY`: Voice similarity setting (default: 0.9)
- OpenAI:
  - `OPENAI_API_KEY`: API key for OpenAI authentication
  - `OPENAI_TTS_MODEL`: OpenAI TTS model to use (default: "tts-1")
  - `OPENAI_TTS_VOICE`: OpenAI TTS voice to use (default: "alloy")
- Deepgram:
  - `DG_API_KEY`: API key for Deepgram authentication
  - `DG_TTS_MODEL_VOICE`: Deepgram TTS model and voice (default: "aura-asteria-en")
- Cartesia:
  - `CARTESIA_API_KEY`: API key for Cartesia authentication
  - `CARTESIA_VOICE_ID`: Voice ID for the Cartesia TTS service
  - `CARTESIA_MODEL_ID`: Model ID for Cartesia (default: "sonic-english")
  - `CARTESIA_VERSION`: API version for Cartesia (default: "2024-06-10")
- `CACHE_DIR`: Directory for caching audio data (default: "cache")

### Supported TTS Providers
1. ElevenLabs
2. OpenAI
3. Deepgram
4. Cartesia

## Technical Details

### TTS Interface
The TTS service uses an abstract base class `TTSInterface` that defines the common interface for all TTS providers. Each provider implements this interface with the following abstract methods:

```python
class TTSInterface(ABC):
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
```


## Example Usage

**Connecting to the WebSocket:**
```javascript
const socket = new WebSocket('ws://localhost:8002/api/v1/ws');

socket.onopen = () => {
  console.log('Connection opened');
};

socket.onmessage = (event) => {
  if (typeof event.data === 'string') {
    const message = JSON.parse(event.data);
    if (message.action === 'done') {
      console.log('Synthesis completed');
    }
  } else {
    console.log('Received binary audio data');
    // Handle audio data (e.g., play it or save it)
  }
};

socket.onclose = (event) => {
  console.log('Connection closed');
};

socket.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

**Sending a Synthesize Message:**
```javascript
const message = {
  action: 'synthesize',
  text: 'Hello, how can I assist you today?'
};
socket.send(JSON.stringify(message));
```

**Sending a Cancel Message:**
```javascript
const message = {
  action: 'cancel'
};
socket.send(JSON.stringify(message));
```

This documentation provides an overview of the Text-to-Speech WebSocket API, including connection details, message formats, events, supported providers, and example usage. The API supports multiple TTS providers and includes configuration options through environment variables.