---
sidebar_position: 5
---

# Guardrails

A proxy server that applies guardrails to requests and responses.

## Info

- **Title:** Guardrails Proxy
- **Description:** A proxy server that applies guardrails to requests and responses.
- **Version:** 1.0.0

## Paths

### `/ {path}`

#### PUT

**Summary:** Proxy Request

**Description:** Proxies incoming requests to the target server, applying guardrails if configured.

**Args:**
- `path` (str): The path of the incoming request.
- `request` (Request): The incoming FastAPI request object.

**Returns:** Response: The proxied response, potentially modified by guardrails.

**Parameters:**
- `path` (string, required): Path

**Responses:**
- `200`: Successful Response
- `422`: Validation Error

#### GET

**Summary:** Proxy Request

**Description:** Proxies incoming requests to the target server, applying guardrails if configured.

**Args:**
- `path` (str): The path of the incoming request.
- `request` (Request): The incoming FastAPI request object.

**Returns:** Response: The proxied response, potentially modified by guardrails.

**Parameters:**
- `path` (string, required): Path

**Responses:**
- `200`: Successful Response
- `422`: Validation Error

#### PATCH

**Summary:** Proxy Request

**Description:** Proxies incoming requests to the target server, applying guardrails if configured.

**Args:**
- `path` (str): The path of the incoming request.
- `request` (Request): The incoming FastAPI request object.

**Returns:** Response: The proxied response, potentially modified by guardrails.

**Parameters:**
- `path` (string, required): Path

**Responses:**
- `200`: Successful Response
- `422`: Validation Error

#### OPTIONS

**Summary:** Proxy Request

**Description:** Proxies incoming requests to the target server, applying guardrails if configured.

**Args:**
- `path` (str): The path of the incoming request.
- `request` (Request): The incoming FastAPI request object.

**Returns:** Response: The proxied response, potentially modified by guardrails.

**Parameters:**
- `path` (string, required): Path

**Responses:**
- `200`: Successful Response
- `422`: Validation Error

#### POST

**Summary:** Proxy Request

**Description:** Proxies incoming requests to the target server, applying guardrails if configured.

**Args:**
- `path` (str): The path of the incoming request.
- `request` (Request): The incoming FastAPI request object.

**Returns:** Response: The proxied response, potentially modified by guardrails.

**Parameters:**
- `path` (string, required): Path

**Responses:**
- `200`: Successful Response
- `422`: Validation Error

#### DELETE

**Summary:** Proxy Request

**Description:** Proxies incoming requests to the target server, applying guardrails if configured.

**Args:**
- `path` (str): The path of the incoming request.
- `request` (Request): The incoming FastAPI request object.

**Returns:** Response: The proxied response, potentially modified by guardrails.

**Parameters:**
- `path` (string, required): Path

**Responses:**
- `200`: Successful Response
- `422`: Validation Error

## Components

### Schemas

#### HTTPValidationError

- **Type:** object
- **Title:** HTTPValidationError

**Properties:**
- `detail` (array of [ValidationError](#validationerror)): Detail

#### ValidationError

- **Type:** object
- **Required:** ["loc", "msg", "type"]
- **Title:** ValidationError

**Properties:**
- `loc` (array of `string` or `integer`): Location
- `msg` (string): Message
- `type` (string): Error Type