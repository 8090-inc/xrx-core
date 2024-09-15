# Orchestrator
The orchestrator module is a central hub that manages and routes data between various components or services in xRx.

## Getting Started

### Prerequisites

Install `Docker`, `Nodejs`, `npm` with [homebrew](https://formulae.brew.sh/) on MacOS or `apt-get update` on Debian/Ubuntu based Linux systems
```bash
brew install node@18
```

To run the unit test under the `test` folder, install `portaudio` on MacOS.
```bash
brew install portaudio
```

## How To Run

### Locally with Docker
```bash
docker build -t xrx-orchestrator:latest .
docker run --rm -it -p 8000:8000 --init xrx-orchestrator:latest
```

### Locally without Docker

```bash
npm install 
npm run dev
```
Once the app/container is up and running, visit the client at [http://localhost:8000](http://localhost:8000)

# How to use

The orchestrator is a central hub that manages and routes data between various components or services in xRx, 
such as the speech-to-text module, the agent, and the text-to-speech module. 

The orchestrator is a websocket server listening on port 8000. It accepts both binary and text messages, and will
send both binary and text messages.

Binary messages are expected to be raw 16khz, 16bit, mono audio data.


### Text message responses json schema:

```json
{
    "role": "user or agent",
    "type": "widget or text",
    "content": "text"
}
```

If the type of response is `widget`, the content may contain [markdown](https://en.wikipedia.org/wiki/Markdown).

