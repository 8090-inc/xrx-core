---
sidebar_position: 7
---

# Changing TTS providers

xRx supports multiple Text-to-Speech (TTS) providers, allowing you to choose the one that best fits your needs. This guide will walk you through the process of changing TTS providers in your xRx deployment.

## Supported TTS Providers

Currently, xRx supports the following TTS providers:

1. Elevenlabs
2. Deepgram
3. OpenAI

## Configuring the TTS Provider

To change the TTS provider, you need to modify the environment variables in your `.env` file. Here's how to do it:

1. Open your `.env` file located at the root of the xRx repository.

2. Locate the TTS-related environment variables:

```
# === Text-to-speech options ===
# TTS provider. Choices are "elevenlabs", "deepgram", "openai", or "cartesia"
TTS_PROVIDER="elevenlabs"
TTS_SAMPLE_RATE="24000"

# Elevenlabs
ELEVENLABS_API_KEY="<Elevenlabs API key>"
ELEVENLABS_VOICE_ID="<Elevenlabs Voice ID>"
...

# Deepgram
DG_API_KEY="<Deepgram API key>"
DG_TTS_MODEL_VOICE="aura-asteria-en"

# OpenAI
OPENAI_API_KEY="<OpenAI API key>"
OPENAI_TTS_MODEL="<OpenAI TTS model>"
OPENAI_TTS_VOICE="<OpenAI TTS voice>"
```

3. Change the `TTS_PROVIDER` value to your desired provider:
   - For Elevenlabs: `TTS_PROVIDER="elevenlabs"`
   - For Deepgram: `TTS_PROVIDER="deepgram"`
   - For OpenAI: `TTS_PROVIDER="openai"`

4. Provide the necessary API keys and configuration for your chosen provider.

## Provider-Specific Configuration

### Elevenlabs

For Elevenlabs, you need to set the following environment variables:

```
ELEVENLABS_API_KEY="<your Elevenlabs API key>"
ELEVENLABS_VOICE_ID="<your chosen Voice ID>"
ELEVENLABS_MODEL_ID="eleven_turbo_v2.5"
ELEVENLABS_VOICE_STABILITY="0.9"
ELEVENLABS_VOICE_SIMILARITY="0.9"
```

You can sign up for an Elevenlabs account and obtain an API key at https://elevenlabs.io/app/sign-up.

### Deepgram

For Deepgram, you need to set the following environment variables:

```
DG_API_KEY="<your Deepgram API key>"
DG_TTS_MODEL_VOICE="aura-asteria-en"
```

You can sign up for a Deepgram account and obtain an API key at https://deepgram.com/.

### OpenAI

For OpenAI, you need to set the following environment variables:

```
OPENAI_API_KEY="<your OpenAI API key>"
OPENAI_TTS_MODEL="<your chosen TTS model>"
OPENAI_TTS_VOICE="<your chosen TTS voice>"
```

You can sign up for an OpenAI account and obtain an API key at https://platform.openai.com/signup.


## Applying Changes

After modifying the `.env` file:

1. Save the changes to your `.env` file.
2. Restart your xRx system for the changes to take effect:

```bash
docker-compose down
docker-compose up --build
```

## Troubleshooting

If you encounter issues after changing the TTS provider:

1. Double-check your `.env` file to ensure all required variables are set correctly.
2. Verify that you have the necessary API keys and they are valid.
3. Check the logs of the TTS service for any error messages:

```bash
docker-compose logs xrx-tts
```

4. Ensure that your chosen TTS provider is properly configured and accessible from your deployment environment.

## Technical Notes

- The default sample rate for all models is 24000Hz. If a model uses a different sample rate, the `.env` variable `TTS_SAMPLE_RATE` should be changed to match the sample rate of the model.
- There is a limit of 4000 characters for the maximum input length sent to the TTS API. This can be adjusted if the TTS API has smaller limits.
- The TTS service implements a caching mechanism to improve performance. Synthesized audio is cached on disk in the `cache` directory.
- Every TTS model is implemented with streaming capabilities for fast responses.

By following these steps, you can easily switch between different TTS providers in your xRx system, allowing you to choose the best option for your specific use case and requirements.

