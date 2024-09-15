# Speech-to-text

A FastAPI application that handles WebSocket connections for speech-to-text (STT) services. It supports multiple STT providers and processes audio data received via WebSocket, transcribing it into text and sending the results back to the client.

This module uses Whisper for ASR.

## Getting Started

### Prerequisites

Install `Docker`, `Python3` and `Pip3` with [homebrew](https://formulae.brew.sh/) on MacOS or `apt-get update` on Debian/Ubuntu based Linux systems
```bash
brew cask install docker
brew install python@3.10
```
### API Keys
- Access to a Groq cloud API. The following environment variables available for Groq LLM usage. Visit https://console.groq.com/docs/quickstart to create your Groq API key
    - `GROQ_STT_API_KEY`
    - `LLM_API_KEY`
- The following environment variables available for the appropriate STT provider.
    - `STT_PROVIDER`
    - `LOG_SPEECH_THRESHOLD`
    - `WHISPER_MODEL`
    - `STT_LANGUAGE_CODE`
---

## How To Run

### Locally with Docker
Ensure to be in the root folder `xrx`
```bash
chmod a+x ../scripts/remove_quotes_from_env_file.sh
../scripts/remove_quotes_from_env_file.sh ../.env
docker build -t xrx-stt:latest .
docker run -it --rm \
--env-file .docker.env \
-p 8001:8001 \
xrx-stt:latest
```
Once the containers are up and running, visit the client at [http://localhost:3000](http://localhost:3000)

### Locally without Docker

#### Setup the Python Virtual Environment.
 ```
 python3 -m venv myenv
 source myenv/bin/activate
```

#### Install requirements
```bash
pip install -r requirements.txt
cd app
uvicorn main:app --reload --port 8001 --env-file ../../.env
```

Now you will then have a websocket server running on [http://localhost:8001/api/v1/ws](http://localhost:8001/api/v1/ws)

---

## Debug
Debugging with FastAPI CLI.

1. Install `python` and `pip`
2. Install `fastapi`
3. Launch the service through `fastapi dev app/main.py --port 8001`
4. The WebSocket will be accessible at `ws://localhost:8001/api/v1/ws`
