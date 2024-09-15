---
sidebar_position: 2
---

# Quick Start

## Introduction

In this quick start, we will walk through the steps to get the xRx system up and running. xRx is designed as a modular system with pluggable components. The core of xRx consists of reasoning agents; a few example reasoning agents are located in the `applications` folder.

For this guide, we will be using the simple agent as our example, but the setup process remains consistent for any reasoning agent you choose to implement.

## Getting Started

### Prerequisites

In order to deploy the xRx system locally, you will need to install a few dependencies. If you are using MacOS, you can install them with the following:

If you do not have [Homebrew](https://brew.sh/) installed, you will need to install it.

```bash
/bin/bash -c "$(curl -fsSL \
https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

You will also need to add Homebrew to your PATH. If you are using bash...

```bash
echo "export PATH=/usr/local/bin:$PATH" >> \
~/.bash_profile && source ~/.bash_profile
```

If you are using zsh...

```bash
echo "export PATH=/usr/local/bin:$PATH" >> \
~/.zshrc && source ~/.zshrc
```

Then verify the installation.

```bash
brew --version
```

To install Docker, you can use Homebrew.

```bash
brew install --cask docker
```

Then verify the installation.

```bash
docker --version
```

Start Docker.

```bash
open -a Docker
```

### Clone the xRx Repository

Clone the `main` branch of the xRx repository using your preferred method.

```bash
git clone https://github.com/8090-inc/xrx.git
```

### External Services Configuration

xRx requires three external services: LLM, Text-to-Speech, and Speech-to-Text. Once you obtain the API keys, configure these services by setting the environment variables in the `.env` file inside the `simple-agent` application.

#### LLMs

We recommend Groq for high token throughput. Sign up at [Groq](https://console.groq.com/docs/quickstart) and obtain an API key.

```
LLM_API_KEY=<your groq api key>
LLM_BASE_URL="https://api.groq.com/openai/v1"
LLM_MODEL_ID="llama3-70b-8192"
```

We recommend the models in the variables above for our repository, but they can be changed to any model that is supported by the LLM provider.

#### Speech to Text

Multiple transcription options are supported in xRx. Currently, you are able to use OpenAI's Whisper model running on Groq Cloud, Deepgram, or a local whisper model. For the easiest setup, we recommend using Groq's Whisper because you will already have an API key from the previous step. If you want to use two different Groq API keys, that is supported as well.

You will need to set two different environment variables for the STT service in your `.env`. See these below:

```
STT_PROVIDER="groq"
GROQ_STT_API_KEY="<your groq api key>"
```

#### Text to Speech

The xRx TTS module supports multiple models for text-to-speech conversion. For this demonstration, we will utilize Elevenlabs, known for its high-quality voice synthesis. To access their service, please register at [Elevenlabs](https://elevenlabs.io/app/sign-up) and obtain an API key. Once you will have the API keys, update the `.env` file as seen below:

```
TTS_PROVIDER="elevenlabs"
ELEVENLABS_API_KEY=<your elevenlabs api key>
ELEVENLABS_VOICE_ID=<your elevenlabs voice id>
```


### How To Run the Simple Agent application

1. You should already be in the `Simple Agent` directory within the `applications` folder. Inside this directory, locate the example `.env` file and input your API keys.

2. Follow the instructions at the `Simple Agent` directory in the `Readme.md` file to install the necessary requirements.

3. Build and run the system using Docker:

```bash
docker-compose up --build
```

3. Visit the xRx Demo client at [http://localhost:3000](http://localhost:3000)

Enjoy exploring and interacting with the xRx system!
