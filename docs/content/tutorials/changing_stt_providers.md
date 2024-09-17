---
sidebar_position: 6
---

# Changing STT providers

xRx supports multiple Speech-to-Text (STT) providers, allowing you to choose the one that best fits your needs. This guide will walk you through the process of changing STT providers in your xRx deployment.

## Supported STT Providers

Currently, xRx supports the following STT providers:

1. Deepgram
2. Groq's Whisper
3. Local Whisper model

## Configuring the STT Provider

To change the STT provider, you need to modify the environment variables in your `.env` file. Here's how to do it:

1. Open your `.env` file located at the root of the xRx repository.

2. Locate the STT-related environment variables:

```
# === Speech-to-text options ===
# STT provider. Choices are "groq", "deepgram", or "faster_whisper"
STT_PROVIDER="deepgram"
STT_SAMPLE_RATE="16000"

# Deepgram
DG_API_KEY="<Deepgram API key>"
```

3. Change the `STT_PROVIDER` value to your desired provider:
   - For Deepgram: `STT_PROVIDER="deepgram"`
   - For Groq's Whisper: `STT_PROVIDER="groq"`
   - For local Whisper model: `STT_PROVIDER="faster_whisper"`

4. Provide the necessary API keys or configuration for your chosen provider.

## Provider-Specific Configuration

### Deepgram

For Deepgram, you need to set the `DG_API_KEY` environment variable:

```
DG_API_KEY="<your Deepgram API key>"
```

You can sign up for a Deepgram account and obtain an API key at https://console.deepgram.com/signup.

### Groq's Whisper

For Groq's Whisper, you need to set the Groq API key:

```
GROQ_STT_API_KEY="<your Groq API key>"
```

Please note, this can be the same or different API key you use for the LLM API.

### Local Whisper Model

For the local Whisper model (faster_whisper), no additional API keys are required. However, ensure that you have the necessary dependencies installed in your environment.

## Applying Changes

After modifying the `.env` file:

1. Save the changes to your `.env` file.
2. Restart your xRx system for the changes to take effect:

```bash
docker-compose down
docker-compose up --build
```

## Troubleshooting

If you encounter issues after changing the STT provider:

1. Double-check your `.env` file to ensure all required variables are set correctly.
2. Verify that you have the necessary API keys and they are valid.
3. Check the logs of the STT service for any error messages:

```bash
docker-compose logs xrx-stt
```

4. Ensure that your chosen STT provider is properly configured and accessible from your deployment environment.

By following these steps, you can easily switch between different STT providers in your xRx system, allowing you to choose the best option for your specific use case and requirements.
