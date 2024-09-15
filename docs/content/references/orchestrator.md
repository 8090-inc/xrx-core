---
sidebar_position: 1
---

# Orchestrator

### Overview
The xRx WebSocket API allows clients to connect to a server for real-time communication. The server handles both text and binary messages, providing functionalities such as speech-to-text (STT), text-to-speech (TTS), and interaction with an agent.

### Endpoint
- **URL:** `/api/v1/ws`
- **Method:** `GET`
- **Protocol:** WebSocket

### Authentication
- **Header:** [x-api-key](https://github.com/8090-inc/xrx/blob/main/orchestrator/src/Index.ts#37%2C29-37%2C29)
- **Value:** [API_KEY](https://github.com/8090-inc/xrx/blob/main/orchestrator/src/Index.ts#12%2C7-12%2C7) from environment variables (default: [123456](https://github.com/8090-inc/xrx/blob/main/orchestrator/src/Index.ts#12%2C44-12%2C44))

### Connection
Upon connecting to the WebSocket endpoint, the server will log the connection and store the session.

### Messages
The server handles two types of messages: text and binary.

#### Text Messages
- **Format:** JSON
- **Fields:**
  - [type](https://github.com/8090-inc/xrx/blob/main/orchestrator/src/Session.ts#1%2C53-1%2C53): `"text"` or `"action"`
  - [content](https://github.com/8090-inc/xrx/blob/main/orchestrator/src/Session.ts#58%2C5-58%2C5): The text content or action details

**Example:**
```json
{
  "type": "text",
  "content": "Hello, how can I help you?"
}
```

#### Binary Messages
- **Format:** Binary data (e.g., audio data)

### Events

#### `message`
- **Description:** Triggered when a message is received from the client.
- **Parameters:**
  - `message`: The message data (text or binary)
  - `isBinary`: Boolean indicating if the message is binary

**Handling Text Messages:**
- If `type` is `"text"`, the server will append the text to the session's chat history and send it to the agent.
- If `type` is `"action"`, the server will send the action to the agent.

**Handling Binary Messages:**
- The server will append the binary data (audio) to the session's speech buffer and process it using VAD (Voice Activity Detection).

#### `close`
- **Description:** Triggered when the client closes the connection.
- **Parameters:**
  - `code`: The close code
  - `reason`: The reason for closing

### Server Responses

#### Text Responses
- **Format:** JSON
- **Fields:**
  - `user`: The user who sent the message
  - `content`: The message content
  - `type`: The type of message (`"text"`, `"audio"`, `"widget"`)

**Example:**
```json
{
  "user": "agent",
  "content": "One moment please...",
  "type": "text"
}
```

#### Binary Responses
- **Format:** Binary data (e.g., audio data)

### Error Handling
- If the session is not found, the server logs an error and does not process the message.
- If the STT or TTS WebSocket is not open, the server attempts to reopen the connection and logs any errors.

### Environment Variables
- `API_KEY`: API key for authentication
- `AGENT_HOST`, `AGENT_PORT`: Configuration for the agent
- `GUARDRAILS_AGENT_HOST`, `GUARDRAILS_AGENT_PORT`: Configuration for the guardrails agent
- `AGENT_WAIT_MS`, `SAMPLE_RATE`, `STT_WAIT_MS`: Timing and sample rate configurations for the STT
- `STT_HOST`, `STT_PORT`, `STT_PATH`: Configuration for the STT WebSocket
- `TTS_HOST`, `TTS_PORT`, `TTS_PATH`: Configuration for the TTS WebSocket
- `INITIAL_RESPONSE`: Initial response message
- `STT_PROVIDER`: STT provider (e.g., `deepgram`)
- `REDIS_HOST`: Configuration for Redis

### Example Usage

**Connecting to the WebSocket:**
```javascript
const socket = new WebSocket('ws://localhost:8000/api/v1/ws');

socket.onopen = () => {
  console.log('Connection opened');
};

socket.onmessage = (event) => {
  if (typeof event.data === 'string') {
    const message = JSON.parse(event.data);
    console.log('Received message:', message);
  } else {
    console.log('Received binary data');
  }
};

socket.onclose = (event) => {
  console.log(`Connection closed: ${event.code} ${event.reason}`);
};

socket.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

**Sending a Text Message:**
```javascript
const message = {
  type: 'text',
  content: 'Hello, how can I help you?'
};
socket.send(JSON.stringify(message));
```

**Sending a Binary Message:**
```javascript
const audioData = new Uint8Array([/* audio data */]);
socket.send(audioData);
```

This documentation provides an overview of the WebSocket API, including connection details, message formats, events, and example usage.