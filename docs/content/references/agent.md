---
sidebar_position: 4
---

# Reasoning Agent

FastAPI Version: 0.1.0

## Endpoints

### Execute Agent

**POST** `/run-reasoning-agent`

Execute the reasoning agent and stream the results.

This endpoint starts a new task for the reasoning agent and returns a streaming response with the agent's output. The task ID is returned in the 'X-Task-ID' header of the response.

#### Request Body

| Field | Type | Description |
|-------|------|-------------|
| messages | array of [Message](#message) | List of messages in the conversation |
| session | object | Session information for the conversation |
| action | object or null | Optional action to be performed by the agent (default: {}) |

#### Responses

- **200**: Successful Response
- **422**: Validation Error

### Cancel Agent

**POST** `/cancel-reasoning-agent/{task_id}`

Cancel a running reasoning agent task.

This endpoint attempts to cancel a task identified by the given task_id. It sets the task status to 'cancelled' in Redis.

#### Parameters

| Name | In | Type | Required | Description |
|------|----|----|----------|-------------|
| task_id | path | string | Yes | The ID of the task to cancel |

#### Responses

- **200**: Successful Response
  - Content: [CancelResponse](#cancelresponse)
- **422**: Validation Error

## Schemas

### AgentRequest

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| messages | array of [Message](#message) | Yes | List of messages in the conversation |
| session | object | No | Session information for the conversation |
| action | object or null | No | Optional action to be performed by the agent (default: {}) |

### CancelResponse

| Field | Type | Required |
|-------|------|----------|
| detail | string | Yes |

### Message

| Field | Type | Required |
|-------|------|----------|
| role | string | Yes |
| content | string | Yes |

### HTTPValidationError

| Field | Type | Description |
|-------|------|-------------|
| detail | array of [ValidationError](#validationerror) | |

### ValidationError

| Field | Type | Description |
|-------|------|-------------|
| loc | array of (string or integer) | Location |
| msg | string | Message |
| type | string | Error Type |