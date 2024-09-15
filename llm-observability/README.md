# Using LLM Observability Frameworks

Currently, the xRx repository supports Langfuse (cloud service and self hosted) and LangSmith as frameworks for LLM observability.

## How to Setup

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

Tracing will automatically then go to LangSmith.

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

### Langfuse (self hosted)

**IMPORTANT: this is the only completely free way we support observability at the moment**

Clone the Langfuse repo [here](https://github.com/langfuse/langfuse)

Because the front end client runs on port 3000 for xRx, you must change the Langfuse port forwarding to a port other than 3000 in your local deployment via docker for Langfuse. You can do this yourself by altering their [docker-compose.yml](https://github.com/langfuse/langfuse/blob/main/docker-compose.yml). Or, we have provide a  `docker-compose.yml` [here](./langfuse/docker-compose.yml) that you can use to start a Langfuse server on a different port (3001).

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
