# Guardrails Proxy

## Overview

This proxy acts as an intermediary between any orchestrator sending text to a reasoning agent and the agent itself. It is responsible for applying various guardrails to the input and output, including but not limited to detecting toxic language.

## How the Proxy Works

The Guardrails Proxy operates as follows:

1. **Request Interception**: The proxy intercepts incoming requests intended for the reasoning agent.

2. **Input Validation**: For configured endpoints (defined in `MONITOR_CONFIG`), the proxy extracts the relevant content from the request body and applies the specified guardrails.

3. **Guardrails Application**: The extracted content is passed through open source models available through the [Guardrails AI Hub](https://hub.guardrailsai.com), which applies the configured checks (e.g., toxic language detection).

4. **Request Forwarding**: If the input passes all guardrails, the proxy forwards the original request to the reasoning agent.

5. **Response Handling**: The proxy receives the response from the reasoning agent and can optionally apply output guardrails (if enabled).

6. **Streaming**: The proxy supports streaming responses, allowing for real-time communication between the client and the server (reasoning agent).

7. **Error Handling**: If any guardrails fail, the proxy returns an error response without forwarding the request to the reasoning agent.

This design allows for flexible and extensible content moderation and validation, ensuring that both inputs to and outputs from the reasoning agent meet specified criteria.

## Getting Started

### Reasoning Agent
Access to a target reasoning agent. The following environment variables are required:

- `AGENT_HOST` `[suggested config: xrx-guardrails]`
- `AGENT_PORT` `[suggested config: 8094]`
- `GUARDRAILS_AGENT_HOST` `[suggested config: xrx-reasoning]`
- `GUARDRAILS_AGENT_PORT` `[suggested config: 8003]`

For information on setting up and running a reasoning agent, please refer to the documentation in the `applications` directory.

  

## Guardrails AI Hub

This proxy utilizes Guardrails AI Hub for content moderation and validation. While the current implementation focuses on toxic language detection, the system is designed to be flexible and can incorporate multiple guardrails. Some examples of additional guardrails that can be implemented include:

- PII (Personally Identifiable Information) detection
- Sentiment analysis
- Language detection
- Content classification
- Custom validation rules

The current configuration uses the ToxicLanguage guard with a threshold of 0.5 and sentence-level validation. However, this can be easily extended to include other guards as needed for your specific use case.

## Configuration

The proxy's configuration is defined in the `main.py` file within the `app` directory. The `MONITOR_CONFIG` dictionary specifies how to extract and validate input for different API endpoints. Here's an example of the configuration structure:

```python
MONITOR_CONFIG = {
    "run-reasoning-agent": {
        "input_keys": {
            "messages": {
                "type": "list",
                "list_index": -1,
                "items": {
                    "type": "object",
                    "field": "content",
                }
            }
        }
    }
}
```

This configuration tells the proxy how to extract the content to be validated from the incoming request body. In this example, for the "run-reasoning-agent" endpoint, it looks for a "messages" key in the request body, which should contain a list. It then extracts the content from the last item in this list.

You can modify this configuration to suit your specific API structure and validation needs. For example, you could add more endpoints or change the structure of the input keys to match your API's request format.

## How To Run
In this implementation, the Guardrails model is downloaded and run locally by default. If you prefer using a managed service instead, please check the documentation at [Guardrails AI](https://www.guardrailsai.com/) for more information.

### Locally with Docker
```bash
docker build -t xrx-guardrails:latest .
docker run -it --rm \
--env-file ./.docker.env \
xrx-guardrails:latest
```

### Locally without Docker

#### Setup the Python Virtual Environment
```bash
python3 -m venv myenv
source myenv/bin/activate
```

#### Install requirements
```bash
pip install -r requirements.txt
guardrails hub install hub://guardrails/toxic_language
cd app
uvicorn main:app --reload --port 8094 --env-file ../../.env
```

If you get the following error, it means you are not in the *app* directory
```
ERROR:    Error loading ASGI app. Could not import module "main".
```

Now you have the app/container up and running at [http://localhost:8094](http://localhost:8094)

### Chat interface for testing

Once you have the API up and running, in a separate terminal, go to `guardrails-proxy/test` directory. 

From there, in another fresh python environment, install the dependencies:

```bash
pip install -r requirements.txt
```

Then run the following command to start the chat interface:

```
python test.py
```

You should see a terminal interface which looks like this:

```
Interactive Guardrails Test. Type 'quit' to exit.
Customer:
```

You can then interact with the proxy via the `Customer:` input in the terminal. This will allow you to test the various guardrails implemented in the Guardrails Proxy, including toxic language detection and any other guardrails you choose to add. Happy testing!

## Extending Guardrails

To add more guardrails or modify existing ones, you can edit the `guard.py` file. The `Guard().use_many()` method allows you to chain multiple guardrails together. For example:

```python
guard = Guard().use_many(
    ToxicLanguage(threshold=0.5, use_local=True, validation_method="sentence", on_fail=OnFailAction.EXCEPTION),
    PIIDetector(on_fail=OnFailAction.EXCEPTION),
    CustomGuardrail(your_parameters)
)
```
To switch to the managed version of guardrails, `use_local` needs to be switched to `False`.

Remember to import any new guardrails you add and adjust the validation logic in `main.py` as needed. You may also need to update the `MONITOR_CONFIG` in `main.py` if your new guardrails require different input structures.