---
sidebar_position: 1
---

# System Architecture

## Modular Components

The xRx system architecture consists of several components that interact with each other to provide build a reasoning based application. Below is a high-level overview of the system:

```mermaid
flowchart TD
    A[Client] <-->|audio/text| B[Orchestrator]
    B -->|Send audio| C[STT]
    C -->|Return text| B
    B <-->|text| G[Guardrail Proxy]
    G <-->|text| D[Agent]
    D[Agent] <-->|text / API requests| F[External Services]
    B -->|Send text| E[TTS]
    E -->|Return audio| B

style A fill:#FFCDD2,stroke:#B71C1C,stroke-width:2px,color:#000000
style B fill:#BBDEFB,stroke:#0D47A1,stroke-width:2px,color:#000000
style C fill:#C8E6C9,stroke:#1B5E20,stroke-width:2px,color:#000000
style D fill:#FFF9C4,stroke:#F57F17,stroke-width:2px,color:#000000
style E fill:#D1C4E9,stroke:#4A148C,stroke-width:2px,color:#000000
style F fill:#FFECB3,stroke:#FF6F00,stroke-width:2px,color:#000000
style G fill:#E1BEE7,stroke:#4A148C,stroke-width:2px,color:#000000
```

- **Client**: Front end app experience which renders the UI and handles websocket communication with the Orchestrator. [See directory here](https://github.com/8090-inc/xrx/blob/main/nextjs-client)
- **Orchestrator**: Manages the flow of data between various AI and traditional software components. [See directory here](https://github.com/8090-inc/xrx/blob/main/orchestrator)
- **STT (Speech-to-Text)**: Converts audio input to text. [See directory here](https://github.com/8090-inc/xrx/blob/main/stt)
- **TTS (Text-to-Speech)**: Converts text responses back to audio. [See directory here](https://github.com/8090-inc/xrx/blob/main/tts)
- **Agent**: Responsible for the "reasoning" system of xRx. [See directory here](https://github.com/8090-inc/xrx/blob/main/reasoning/shopify-agent)
- **Guardrails Proxy**: A safety layer for the reasoning system. [See directory here](https://github.com/8090-inc/xrx/blob/main/guardrails-proxy)

## Information Flow

These components then communicate via the following sequence diagram

```mermaid

sequenceDiagram
    participant Client
    participant Orchestrator
    participant STT
    participant Agent
    participant TTS

    Client->> Orchestrator: Send audio on websockets port 8000
    Orchestrator->>STT: Send audio on websockets port 8001
    STT ->>Orchestrator: Return text
    Orchestrator->>Agent: Send text on port 8003
    Agent->>Orchestrator: Return text
    Orchestrator->>TTS: Send text on port 8002
    TTS ->>Orchestrator: Return audio
    Orchestrator->>Client: Return audio, text, and application widgets
```

## Deployment Specifics

xRx's deployment is designed to be modular in nature. This means that you can swap out any component of the system with your own custom implementation. The entire system is defined as a single docker-compose file with a single connected network. This allows for easy swapping of components and deployment to a variety of different environments.

Each system component is defined as a docker image. The docker-compose file located in the application folder will then start each component and connect it to the same network.
