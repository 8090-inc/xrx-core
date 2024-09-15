---
sidebar_position: 4
---

# Build Your Own Reasoning Application

In this tutorial we will see how to create an application with a custom reasoning agent. Any reasoning agent which is built in Python can be used with xRx.

We will use xRx's blank reasoning agent as a template for building your own reasoning agent.

Let's walk through how to use this blank agent...

## Clone the repository

```bash
git clone https://github.com/8090-inc/xRx.git
cd xRx
```

## Rename the template directory

The blank agent code can be found in the `applications/template-agent` directory.

It is a good idea to rename this directory to something more descriptive. For example, if you are building a reasoning agent to help with customer support, you might rename the directory to `applications/customer-support-agent`.

```bash
mv applications/template-agent applications/customer-support-agent
```

## Implement your reasoning agent

The file `applications/customer-support-agent/app/agent/executor.py` is where you will implement your reasoning agent.

Inside that file, there is a single function called `single_turn_agent`. This function is called each time a post request is sent to the reasoning agent.

Here is the code before implementation:
```python
def single_turn_agent(messages: List[dict]) -> str:

    # REASONING CODE GOES HERE

    message = {
        "role": "assistant",
        "content": "I'm a reasoning agent. Please implement me!"
    }
    out = {
        "messages": [message],
        "node": "CustomerResponse",
        "output": message['content'],
    }
    return out
```

**Note**: the output dictionary containing "messages" is always required for storing conversational history. The "node" and "output" are required if you want to send audio responses to the front end. "CustomerResponse" is a special node name which the xRx orchestrator will always send to the front end in order to play audio to the end user.

Here is what the code might look like after implementation:

```python
...
from agent.utils.llm import initialize_llm_client
...
llm_client = initialize_llm_client()
...
def single_turn_agent(messages: List[dict]) -> str:

    resp = llm_client.chat.completions.create(
        model=os.environ['LLM_MODEL_ID'],
        messages=messages,
        temperature=0.0,
    )
    message = {
        "role": "assistant",
        "content": resp.choices[0].message.content
    }
    out = {
        "messages": [message],
        "node": "CustomerResponse",
        "output": message['content'],
    }
    return out
```

## Test your reasoning agent

You can test your reasoning agent by running the following commands in separate terminals.

First, start the FastAPI server which serves your reasoning agent.

```bash
cd app
uvicorn main:app --port 8003 --reload
```

Then in another terminal, run the interactive CLI testing script which has been provided.

```bash
cd test
python test_agent.py
```

You should see an output which resembles the following:

```
python test/test_agent.py

Interactive Agent Test. Type 'quit' to exit.
Customer: hi
{'messages': [{'role': 'assistant', 'content': "I'm a reasoning agent. Please implement me!"}], 'node': 'CustomerResponse', 'output': "I'm a reasoning agent. Please implement me!", 'session': {'id': '391a6959-9e4a-4426-a227-73e428550328'}}
Customer: tell me something fun
{'messages': [{'role': 'assistant', 'content': "I'm a reasoning agent. Please implement me!"}], 'node': 'CustomerResponse', 'output': "I'm a reasoning agent. Please implement me!", 'session': {'id': '391a6959-9e4a-4426-a227-73e428550328'}}
Customer: quit
```

## Build a custom UI

To build custom widgets that will be displayed in the UI, check out the tutorial [Create your own Widgets](./create_your_own_widgets).

## Create your .env file

You will need to have a customized `.env` file to store your API keys and the path to your reasoning agent.

A `.env` template is already provided in the folder directory. Here is an example of what one of these will look like.

```
# === LLM options ===
LLM_API_KEY="<your Api Key>"
LLM_BASE_URL="https://api.groq.com/openai/v1"
LLM_MODEL_ID="llama3-70b-8192"

# === Agent options ===
INITIAL_RESPONSE="Hello! How can I help you?"

# === LLM observability options ===
LLM_OBSERVABILITY_LIBRARY="none"

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


## Deploy the xRx system

Once you have your reasoning agent implemented and your `.env` file created, you can deploy the xRx system by running the following command to deploy all the necessary containers.

Make sure you are in the customer-support-agent directory when running this command.

```bash
docker compose up --build
```