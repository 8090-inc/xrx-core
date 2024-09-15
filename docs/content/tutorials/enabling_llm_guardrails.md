---
sidebar_position: 5
---

# Enabling LLM Guardrails

LLM guardrails are an important feature in the xRx system that help ensure the safety and reliability of AI interactions. This guide will walk you through the process of enabling and configuring LLM guardrails for your xRx deployment.

## Overview

The xRx system uses a Guardrails Proxy to implement safety measures for input and output processing. This proxy acts as an intermediary between the orchestrator and the reasoning agent, applying various checks such as toxic language detection.

## Setup

To enable LLM guardrails, you need to configure the orchestrator to use the Guardrails Proxy instead of connecting directly to the reasoning agent. Here's how to do it:

1. Open the `.env` file in the root directory of your project.
   * *If you don't have a `.env` file, you will need to create one in the root directory of your project with the necessary environment variables. [Here](https://github.com/8090-inc/xrx/blob/main/config/env-examples/env.guardrails) is an example of an `.env` file with the required variables set.*

2. Update or add the following environment variables:

   ```
   AGENT_HOST="xrx-guardrails"
   AGENT_PORT="8094"
   GUARDRAILS_AGENT_HOST="xrx-reasoning"
   GUARDRAILS_AGENT_PORT="8003"
   ```

   This configuration tells the orchestrator to connect to the Guardrails Proxy (`xrx-guardrails`) instead of the reasoning agent directly. It also specifies the host and port for the actual reasoning agent (`xrx-reasoning`) that the Guardrails Proxy will communicate with.

3. Save the `.env` file.

To apply these changes, rebuild and restart your containers:

```bash
docker compose up --build
```

## Advanced Configuration

### Monitoring specific fields

The Guardrails Proxy can be configured to monitor specific endpoints and apply different checks. To customize the guardrails:

1. Open the `guardrails-proxy/app/main.py` file.

2. Locate the `MONITOR_CONFIG` dictionary. This defines which endpoints are monitored and how to extract content for validation.

3. Modify or add entries to suit your API structure. For example:

   ```python
    MONITOR_CONFIG = {
        "my-custom-endpoint": {
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

   This configuration tells the proxy to monitor the input body of "my-custom-endpoint" endpoint, extract content from the last message in the input request, and apply guardrails to the "content" field of the response.


### Customized guardrails

For more advanced guardrails or custom checks, you can:

1. To add or modify guardrails, edit the `guardrails-proxy/app/guard.py` file. You can chain multiple guardrails using the `Guard().use_many()` method.
2. Implement additional guardrail models from the [Guardrails AI Hub](https://hub.guardrailsai.com).
3. Create custom guardrail classes in the `guard.py` file.
4. Adjust the proxy's behavior in `main.py` to handle different types of requests or responses.

By following these steps, you can effectively enable and customize LLM guardrails in your xRx system, enhancing the safety and reliability of your AI interactions.
