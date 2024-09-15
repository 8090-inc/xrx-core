"""
This module implements a FastAPI-based proxy server with guardrails functionality.
It intercepts requests, applies input validation, and optionally applies output validation.
"""

import os
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
import guard
import logging
import json
from dotenv import load_dotenv
import httpx
import nltk


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

# start the FastAPI app
app = FastAPI(
    title="Guardrails Proxy",
    description="A proxy server that applies guardrails to requests and responses.",
    version="1.0.0"
)

load_dotenv()
AGENT_HOST = os.getenv("GUARDRAILS_AGENT_HOST", '0.0.0.0')
AGENT_PORT = os.getenv("GUARDRAILS_AGENT_PORT", '8003')

# Configuration for monitoring
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

def extract_value(data, config):
    """
    Extracts a value from nested data structures based on the provided configuration.

    Args:
        data (dict): The data structure to extract from.
        config (dict): Configuration specifying how to extract the value.

    Returns:
        The extracted value.
    """
    if config["type"] == "list":
        index = config.get("list_index", -1)
        item_config = config["items"]
        item_data = data[index]
        if item_config["type"] == "object":
            field = item_config["field"]
            return item_data[field]
        return item_data
    elif config["type"] == "object":
        field = config["field"]
        return data[field]
    return data

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_request(path: str, request: Request):
    """
    Proxies incoming requests to the target server, applying guardrails if configured.

    Args:
        path (str): The path of the incoming request.
        request (Request): The incoming FastAPI request object.

    Returns:
        Response: The proxied response, potentially modified by guardrails.
    """

    # get base data from the request
    logger.info(f"Proxying request to {request.url.path} with method {request.method}")

    # grab initial headers
    headers = dict(request.headers)
    headers = {k.lower(): v for k, v in headers.items()}
    base_server_url = f"http://{AGENT_HOST}:{AGENT_PORT}"
    request_server_url = httpx.URL(path=path, query=request.url.query.encode("utf-8"))
    logger.info(f"Proxy URL: {base_server_url}")

    # stream the response out
    if path in MONITOR_CONFIG:
        try:
            logger.info(f"Using guardrails for {path}")

            # get the information from the request
            body = await request.json()
            logger.info(f"Input body: {body}")

            # start by validating the input text only
            input_guard = await validate_input(path, body, headers)
            if input_guard:
                return StreamingResponse(content=iter([input_guard]), status_code=200)
            
            # Increase timeout and set limits
            server_client = httpx.AsyncClient(
                base_url=base_server_url,
                timeout=60.0,
            )
            server_request = server_client.build_request(
                method=request.method,
                url=request_server_url,
                headers=headers,
                content=request.stream()
            )
            try:
                server_side_stream = await server_client.send(server_request, stream=True)
            except httpx.ReadTimeout:
                logger.error("ReadTimeout error when connecting to target server")
                return StreamingResponse(content=iter([json.dumps({"error": "Target server timed out"})]), status_code=504)
            except httpx.ConnectError:
                logger.error("Unable to connect to target server")
                return StreamingResponse(content=iter([json.dumps({"error": "Unable to connect to target server"})]), status_code=502)
            
            # Yield the response chunks
            async def stream_response():
                async for chunk in server_side_stream.aiter_bytes():
                    logger.info(f"chunk sent: {chunk}")
                    # TODO: add output validation here
                    yield chunk
            
            # output the response as a streaming object with the server side headers
            response = StreamingResponse(stream_response(), media_type="text/event-stream", headers=server_side_stream.headers)
            return response

        except Exception as e:
            logger.exception(f"Error in stream_guardrails: {e}")
            return StreamingResponse(content=iter([json.dumps({"error": str(e)})]), status_code=500)

    # otherwise simply pass through the response without guardrails
    else:
        logger.info(f"Not using guardrails for {path}")
        async with httpx.AsyncClient(base_url=base_server_url) as client:
            response = await client.request(
                method=request.method,
                url=request_server_url,
                headers=headers,
                content=await request.body()
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )

async def validate_input(path, body, headers):
    """
    Validates the input of a request using configured guardrails.

    Args:
        path (str): The path of the request.
        body (dict): The request body.
        headers (dict): The request headers.

    Returns:
        str or None: A JSON string with validation errors if validation fails, None otherwise.
    """
    
    # Get the session data from the body to be returned later
    session_data = body.get('session', {})

    # start by extracting the necessary information from the body of the post request
    input_keys = MONITOR_CONFIG[path].get("input_keys", {})
    for key, config in input_keys.items():
        if key in body:
            extracted_value = extract_value(body[key], config)

            # now run the guardrails specified
            logging.info(f"validating the following input text: {json.dumps(extracted_value)}")
            input_guardrails = json.loads(guard.validate_text(json.dumps(extracted_value)))
            logging.info(f"input_guardrails: {input_guardrails}")

            # if the guardrails fail, return the error
            if not input_guardrails['validation_passed']:
                logging.error(f"Input Guardrails validation failed: {input_guardrails}")
                output = {
                    'guardrails': [input_guardrails],
                    'session': session_data,
                }
                return f"data: {json.dumps(output)}\n\n"
    return None

async def validate_output(chunk):
    """
    Validates the output chunk of a response.

    Args:
        chunk (bytes): A chunk of the response content.

    Returns:
        None
    """
    # TODO: Implement output validation
    pass