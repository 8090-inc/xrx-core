---
sidebar_position: 2
---

# Quick Start

## Introduction

In this quick start, we will walk through the steps to get the xRx system up and running. xRx is designed as a modular system with pluggable components, with the core consisting of the reasoning agent. You only need to code a reasoning flow, and xRx will automatically create an application that can listen, speak, and display custom UI components.

For this guide, we will be using the simple agent as our example, but the setup process remains consistent for any reasoning agent you choose to implement.

## Components

The xRx system is designed with a modular architecture, separating the core framework from specific applications. This design allows for greater flexibility and customization in application development.

#### Application
- The application layer consists of a Next.js front-end client and a reasoning agent, working together to process user inputs and generate responses through interaction with the xRx Core components.

#### xRx Core
- The xRx Core provides the foundation of the system, including an orchestrator for managing communications, TTS and STT services for audio processing, a React client library for UI development, and an agent framework for building reasoning agents. These components are designed to be reusable across different applications.

This modular structure allows developers to easily customize and extend xRx for their specific needs while benefiting from a solid, tested foundation.

## Getting Started

### Prerequisites

To deploy the xRx system locally, you'll need to install a few dependencies. If you're using macOS, you can install them with the following:

If you don't have [Homebrew](https://brew.sh/) installed, you'll need to install it:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Add Homebrew to your PATH. For bash:

```bash
echo "export PATH=/usr/local/bin:$PATH" >> ~/.bash_profile && source ~/.bash_profile
```

For zsh:

```bash
echo "export PATH=/usr/local/bin:$PATH" >> ~/.zshrc && source ~/.zshrc
```

Verify the installation:

```bash
brew --version
```

Install Docker using Homebrew:

```bash
brew install --cask docker
```

Verify the Docker installation:

```bash
docker --version
```

Start Docker:

```bash
open -a Docker
```

## Clone the xRx Repository

Clone the repository with its submodules using the following command:

```bash
git clone --recursive https://github.com/8090-inc/xrx-sample-apps.git
```

Navigate to the cloned repository:

```bash
cd xrx-sample-apps
```

> **Note:** The `--recursive` flag is crucial here. It ensures that you also clone the xrx-core submodule, which contains the fundamental building blocks of the xRx framework. Without this, your project won't have access to the core functionalities it needs.

If you've already cloned the repository without the `--recursive` flag, or if you need to update the submodule later, you can use:

```bash
git submodule update --init --recursive
```

## External Services Configuration

xRx requires three external services: LLM, Text-to-Speech, and Speech-to-Text. Configure these services by setting the environment variables in the `.env` file inside the `simple-agent` application.

### LLMs

We recommend Groq for high token throughput. Sign up at [Groq](https://console.groq.com/docs/quickstart) and obtain an API key.

```
LLM_API_KEY=<your groq api key>
LLM_BASE_URL="https://api.groq.com/openai/v1"
LLM_MODEL_ID="llama3-70b-8192"
```

We recommend the models in the variables above for our repository, but they can be changed to any model that is supported by the LLM provider.

### Speech to Text

Multiple transcription options are supported in xRx. Currently, you can use OpenAI's Whisper model running on Groq Cloud, Deepgram, or a local whisper model. For the easiest setup, we recommend using Groq's Whisper because you will already have an API key from the previous step. If you want to use two different Groq API keys, that is supported as well.

Set the following environment variables for the STT service in your `.env`:

```
STT_PROVIDER="groq"
GROQ_STT_API_KEY="<your groq api key>"
```

### Text to Speech

The xRx TTS module supports multiple models for text-to-speech conversion. For this demonstration, we will utilize Elevenlabs, known for its high-quality voice synthesis. Register at [Elevenlabs](https://elevenlabs.io/app/sign-up) and obtain an API key. Update the `.env` file as seen below:

```
TTS_PROVIDER="elevenlabs"
ELEVENLABS_API_KEY=<your elevenlabs api key>
ELEVENLABS_VOICE_ID=<your elevenlabs voice id>
```

## How To Run the Simple Agent application

1. Navigate to the `Simple Agent` directory within the `applications` folder. Inside this directory, locate the example `.env` file and input your API keys.

2. Follow the instructions in the `Readme.md` file to install the necessary requirements.

3. Build and run the system using Docker:

```bash
docker-compose up --build
```

4. Access the xRx Demo client at [http://localhost:3000](http://localhost:3000)

Enjoy exploring and interacting with the xRx system!

## Contributing

We welcome contributions to the xRx framework and its sample applications. If you have any suggestions or improvements, please follow these steps:

1. Open a new issue on GitHub describing the proposed change or improvement
2. Fork the repository
3. Create a new branch for your feature
4. Commit your changes
5. Push to your branch
6. Create a pull request, referencing the issue you created

> **Note:** Pull requests not backed by published issues will not be considered. This process ensures that all contributions are discussed and aligned with the project's goals before implementation.