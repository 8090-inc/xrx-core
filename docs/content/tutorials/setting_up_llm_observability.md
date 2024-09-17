---
sidebar_position: 5
---

# Enabling LLM Observability

**Through our own experimentation and development, we have found that observability is a critical component of debugging effective reasoning systems. It is highly recommended that you take advantage of this feature of the xRx repo to save yourself debugging time.**

Currently, the xRx repository supports Langfuse (cloud service and self hosted) and LangSmith as frameworks for LLM observability.

## Infrastructure Setup

### Langfuse (self hosted)

**IMPORTANT: this is the only completely free way we support observability at the moment**

Clone the Langfuse repo [here](https://github.com/langfuse/langfuse)

Because the front end client runs on port 3000 for xRx, you must change the Langfuse port forwarding to a port other than 3000 in your local deployment via docker for Langfuse. You can do this yourself by altering their [docker-compose.yml](https://github.com/langfuse/langfuse/blob/main/docker-compose.yml). Or, we have provide a  `docker-compose.yml` [here](https://github.com/8090-inc/xrx/blob/main/llm-observability/langfuse/docker-compose.yml) that you can use to start a Langfuse server on a different port (3001).

Run `docker compose up` to start the Langfuse server

Go to http://localhost:3001 to access the Langfuse dashboard. Create an account and create a new project. Then create an API key for that project.

In the `.env` file, set the following environment variables:

```
LLM_OBSERVABILITY_LIBRARY="langfuse"
LANGFUSE_SECRET_KEY="<your Langfuse Secret key>"
LANGFUSE_PUBLIC_KEY="<your Langfuse Public key>"
LANGFUSE_HOST="http://host.docker.internal:3001"
```

Tracing will then be sent to your own Langfuse instance hosted on your local machine.

### Langfuse (cloud hosted via Langfuse)

Ensure you have an account created [here](https://us.cloud.langfuse.com)

In the `.env` file, set the following environment variables:

```
LLM_OBSERVABILITY_LIBRARY="langfuse"
LANGFUSE_SECRET_KEY="<your Langfuse Secret key>"
LANGFUSE_PUBLIC_KEY="<your Langfuse Public key>"
LANGFUSE_HOST="https://us.cloud.langfuse.com"
```

Tracing will automatically then go to the Langfuse cloud hosted service.

### LangSmith

Ensure you have an account created [here](https://smith.langchain.com)

In the `.env` file, set the following environment variables:

```
LLM_OBSERVABILITY_LIBRARY="langsmith"
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY="<your Langsmith API key>"
LANGCHAIN_PROJECT= "<your Langsmith project name>"
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
```

Traces will be automatically sent to LangSmith.

### Disabling Observability (not recommended)

If you would like to disable observability, you can do so by setting the following environment variable:

```
LLM_OBSERVABILITY_LIBRARY="none"
```

### Example .env file

An example .env file which has been enabled for using a local Langfuse instance can be found [here](https://github.com/8090-inc/xrx/blob/main/config/env-examples/env.langfuse).

```
# === LLM options ===
LLM_API_KEY="<your Api Key>"
LLM_BASE_URL="https://api.groq.com/openai/v1"
LLM_MODEL_ID="llama3-70b-8192"

# === Agent options ===
INITIAL_RESPONSE="Hello! How can I help you?"

# === LLM observability options ===
# note: make the host domain "localhost" if you are running outside of docker compose
LANGFUSE_HOST_DOMAIN="host.docker.internal"
LANGFUSE_SECRET_KEY="<your Langfuse secret key>"
LANGFUSE_PUBLIC_KEY="<your Langfuse public key>"
LANGFUSE_HOST="http://${LANGFUSE_HOST_DOMAIN}:3001"

# === Text-to-speech options ===
TTS_PROVIDER="elevenlabs"
ELEVENLABS_API_KEY="<your Elevenlabs xi_api_key>"
ELEVENLABS_VOICE_ID="<your Elevenlabs voice_id>"

# === Speech-to-text options ===
# STT provider. Choices are "groq, "deepgram", or "faster_whisper"
STT_PROVIDER="deepgram"

# Deepgram
DG_API_KEY="<Deepgram API key>"
```

## Alter Reasoning Code

### LLM Clients

xRx reasoning agents are designed to be observable by default. To ensure observability, follow these steps:

1. **Use an OpenAI API Compatible Endpoint**: Ensure that any LLM used in the reasoning agent is accessed via an OpenAI API compatible endpoint.

2. **Initialize LLM Clients with Tracing**: Utilize the provided utility function to enable tracing. This function is part of the `initialize_llm_client()` method in the reasoning agent.

   - You can find the code for this function in [this file](https://github.com/8090-inc/xrx/blob/develop/reasoning/simple-agent/app/agent/utils/llm.py).

3. **Ensure Tracing for All LLM Calls**: By initializing all LLM clients with the `initialize_llm_client()` function, tracing will be enabled for all LLM calls.

Here is an example of how to use this function:

```python
from agent.utils.llm import initialize_llm_client

llm_client = initialize_llm_client()
...
response = llm_client.chat.completions.create(
    model=llm_model_id,
    messages=messages,
    temperature=0.9,
)
```

> **Note:** Based on if you need an async or sync LLM client, you would need to modify the `initialize_llm_client()` function to get the appropriate OpenAI client.

### Other tracing elements

For the components of a reasoning system that do not directly call an LLM (e.g., tool calls, orchestration, session operations, etc.), you can use the `observability_decorator` function decorator to ensure that tracing is enabled for these functions. The code for this decorator can be found in [this file](https://github.com/8090-inc/xrx/blob/develop/reasoning/simple-agent/app/agent/utils/llm.py). This decorator is compatible with LangSmith, Langfuse, and "none" (no observability).

We highly recommend always using this decorator, even if you are not currently implementing observability. This will allow you to "switch on" observability at any point in the future. 

Here is an example of how to use this decorator:

```python
from agent.utils.llm import observability_decorator

@observability_decorator(name="higher_than_2")
def higher_than_2(x: int):
    return x > 2
```
