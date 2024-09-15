import WebSocket from 'ws'; // import the WebSocket type from the 'ws' module
import { v4 as uuidv4 } from 'uuid';
import { FastifyInstance } from 'fastify';
import CancelablePromiseQueue from './CancelablePromiseQueue';
import 'dotenv/config'
import { configDotenv } from 'dotenv';
configDotenv({ path: '../.env', override: true });

// eslint-disable-next-line @typescript-eslint/no-var-requires
const VAD = require('node-vad');

const STT_HOST = process.env['STT_HOST'] || 'xrx-stt';
const STT_PORT = parseInt(process.env['STT_PORT'] || '8001');
const STT_PATH = process.env['STT_PATH'] || '/api/v1/ws';

const TTS_HOST = process.env['TTS_HOST'] || 'xrx-tts';
const TTS_PORT = parseInt(process.env['TTS_PORT'] || '8002');
const TTS_PATH = process.env['TTS_PATH'] || '/api/v1/ws';

const AGENT_HOST = process.env['AGENT_HOST'] || 'xrx-reasoning';
const AGENT_PORT = parseInt(process.env['AGENT_PORT'] || '8003');
const AGENT_PATH = process.env['AGENT_PATH'] || '/run-reasoning-agent';
const AGENT_CANCEL_PATH = process.env['AGENT_CANCEL_PATH'] || '/cancel-reasoning-agent';

const AGENT_WAIT_MS = parseInt(process.env['AGENT_WAIT_MS'] || '100');
const SAMPLE_RATE = parseInt(process.env['SAMPLE_RATE'] || '16000');
const STT_WAIT_MS = parseInt(process.env['STT_WAIT_MS'] || '250');

const INITIAL_RESPONSE = (process.env['INITIAL_RESPONSE'] || '');
const STT_PROVIDER = (process.env['STT_PROVIDER'] || '');

const MAX_AGENT_MESSAGES = parseInt(process.env['MAX_AGENT_MESSAGES'] || '20');     

const vad = new VAD(VAD.Mode.VERY_AGGRESSIVE);

class ChatMessage {
    role: string;
    content: string;

    constructor() {
        this.role = '';
        this.content = '';
    }
}

export class Session {
    sttWebSocket: WebSocket;
    ttsWebSocket: WebSocket;
    dictionary: { [key: string]: string };
    guid: string;
    chatHistory: ChatMessage[];
    sessionDict: { [key: string]: string };
    inputBuffer: string;
    speechBuffer: Buffer;
    silenceDuration: number;
    lastVoiceTime: Date;
    server: FastifyInstance;
    receivedVoice: boolean;
    waitingForAgent: boolean;
    agentQueue: CancelablePromiseQueue;
    sentInitialResponse: boolean;
    currentTaskId: string | null;
    isTTSStreaming: boolean;
    agentResponseCache: {type: string, agentResponse: string, modality: string}[];  

    public audioResponse: (audio:Buffer) => void;
    public textResponse: (user:string, content:string, type:string) => void;

    constructor(
        server: FastifyInstance,
        audioResponse: (audio:Buffer) => void, 
        textResponse: (user:string, content:string, type:string) => void
    )
    {
        this.server = server;
        this.dictionary = {};
        this.guid = uuidv4();
        this.chatHistory = [];
        this.sessionDict = {
            guid: this.guid
        };
        this.inputBuffer = '';
        this.silenceDuration = 0;
        this.speechBuffer = Buffer.alloc(0);
        this.audioResponse = audioResponse;
        this.textResponse = textResponse;
        this.receivedVoice = false;
        this.waitingForAgent = false;
        this.agentQueue = new CancelablePromiseQueue();
        this.sentInitialResponse = false;
        this.lastVoiceTime = new Date();
        this.currentTaskId = null;
        this.isTTSStreaming = false;
        this.agentResponseCache = [];

        // configure STT module
        this.sttWebSocket = this.openSTT();
        this.sttWebSocket.onopen = () => {
            this.server.log.debug('STT WebSocket opened');
            this.sendInitialResponse();
        }

        // configure TTS module
        this.ttsWebSocket = this.openTTS();
        this.ttsWebSocket.onopen = () => {
            this.server.log.debug('TTS WebSocket opened');
            this.sendInitialResponse();
        }
    }

    async openSTTAndAwaitConnection(): Promise<void> {
        const sttWebSocket = this.openSTT();
        await new Promise<void>((resolve, reject) => {
            sttWebSocket.onopen = () => {
                this.server.log.debug('STT WebSocket connection successfully opened.');
                resolve();
            };
            sttWebSocket.onerror = (err) => {
                this.server.log.error(`Error opening STT WebSocket: ${err.message}`);
                reject(err);
            };
        });
    }

    async openTTSAndAwaitConnection(): Promise<void> {
        const ttsWebSocket = this.openTTS();
        await new Promise<void>((resolve, reject) => {
            ttsWebSocket.onopen = () => {
                this.server.log.debug('TTS WebSocket connection successfully opened.');
                resolve();
            };
            ttsWebSocket.onerror = (err) => {
                this.server.log.error(`Error opening TTS WebSocket: ${err.message}`);
                reject(err);
            };
        });
    }

    openSTT = (): WebSocket => {
        this.server.log.debug(`STT Opening WebSocket:ws://${STT_HOST}:${STT_PORT}${STT_PATH}`);
        this.sttWebSocket = new WebSocket(`ws://${STT_HOST}:${STT_PORT}${STT_PATH}`);
        this.sttWebSocket.onmessage = this.sttOnMessage;
        this.sttWebSocket.onclose = () => this.server.log.debug('STT WebSocket closed');
        this.sttWebSocket.onerror = (err) => this.server.log.error(`STT WebSocket error: ${err.message}`);
        return this.sttWebSocket;
    }

    openTTS = (): WebSocket => {
        this.server.log.debug(`TTS Opening WebSocket:ws://${TTS_HOST}:${TTS_PORT}${TTS_PATH}`);
        this.ttsWebSocket = new WebSocket(`ws://${TTS_HOST}:${TTS_PORT}${TTS_PATH}`);
        this.ttsWebSocket.onmessage = this.ttsOnMessage;

        this.ttsWebSocket.onclose = () => this.server.log.debug('TTS WebSocket closed');
        this.ttsWebSocket.onerror = (err) => this.server.log.error(`TTS WebSocket error: ${err.message}`);
        return this.ttsWebSocket;
    }

    close = (): void => {
        this.sttWebSocket.close();
        this.ttsWebSocket.close();
    }

    cancelAllAgentActivity = async () => {
        this.server.log.debug('Cancelling all agent activity');
        this.ttsWebSocket.send(JSON.stringify({'action': 'cancel'}));
        this.textResponse('system', 'clear_audio_buffer', 'action');

        // Check for interruption and cancel the current agent task
        if (this.waitingForAgent && this.currentTaskId) {
            this.server.log.debug('Interruption detected, cancelling current agent task');
            await this.cancelAgentTask(this.currentTaskId, this.chatHistory);
            this.currentTaskId = null; // Reset task ID after cancellation
            this.setAgentEnded();  // Reset waitingForAgent flag
        }
    }

    sttOnMessage = async (event: WebSocket.MessageEvent) => {
        this.server.log.debug(`Received from STT: ${event.data}`);
        // detect if binary or text
        if (typeof event.data === 'string') {
            // handle text message
            this.server.log.debug(`Received from STT: ${event.data}`);
            this.inputBuffer += event.data;
            this.inputBuffer = this.inputBuffer.trim() + " "; 

            if(this.inputBuffer === '') {
                return;
            }

            await this.cancelAllAgentActivity();

            // if the current time is greater than the last voice time + AGENT_WAIT_MS
            // then send the chat history to the agent
            
            if (STT_PROVIDER === 'deepgram' || 
                new Date().getTime() > this.lastVoiceTime.getTime() + AGENT_WAIT_MS
            ) {
                this.chatHistory.push({role: 'user', content: this.inputBuffer.trim() });
                this.textResponse('user', this.inputBuffer.trim(), 'audio');
                this.inputBuffer = '';

                const chatJob = () => new Promise<void>((resolve, reject) => {
                    const performJob = async () => {
                        try {
                            await this.sendChatHistoryToAgent('audio');
                            resolve();
                        } catch(error) {
                            this.server.log.debug(`Error in agentQueue: ${(error as Error).message}`);
                            reject(error);
                        }
                    };
                    performJob();
                });
                this.agentQueue.add(chatJob, () => {
                    this.textResponse('agent', 'One moment please...', 'audio');
                    this.synthesizeText('One moment please');
                });
            }
        } else {
            // This should never occur, as STT should only return text
            this.server.log.debug(`Received binary message: ${event.data}`);
        }
    };

    ttsOnMessage = async (event: WebSocket.MessageEvent) => {
        // detect that the event.data is not a string and then send it to the client
        if (typeof event.data !== 'string') {
            const bufferData = Buffer.from(event.data as Buffer);
            this.audioResponse(bufferData);
        } else {
            this.server.log.debug(`Received from TTS: ${event.data}`);
            const data = JSON.parse(event.data);
            if(data.action === 'done') {
                this.server.log.debug(`TTS done, sending cached agent responses`);
                this.isTTSStreaming = false;
                this.agentResponseCache.forEach((response) => {
                    this.handleAgentResponse(response.type, response.agentResponse, response.modality);
                });
                this.agentResponseCache = [];
                this.textResponse('system', 'audio_generation_done', 'action'); // Send a signal to the client that audio generation is done
            }
        }
    };

    sendInitialResponse = (): void => {
        if(INITIAL_RESPONSE && this.sentInitialResponse === false
            && this.sttWebSocket.readyState === WebSocket.OPEN) 
        {
            console.log('initial response sent to STT')
            this.textResponse('agent', INITIAL_RESPONSE, 'text');
            this.sentInitialResponse = true;
        }
    }

    public sendActionToAgent = async (tool:string, parameters: string, modality: string) => {
        const action = {
            'type': 'tool',
            'details': {
                'tool': tool,
                'parameters': JSON.parse(parameters)
            }
        }
        this.server.log.debug(`Sending action to agent: ${JSON.stringify(action)}`);
        await this.sendChatHistoryToAgent(modality, action);
    }

    private synthesizeText(text:string) {
        this.ttsWebSocket.send(JSON.stringify({'action': 'synthesize', 'text': text}));
        this.isTTSStreaming = true;
    }

    private async handleAgentResponse(type: string, agentResponse: string, modality:string): Promise<void> {
        if(this.isTTSStreaming) {
            this.server.log.debug(`TTS is streaming, cache agent responses until not streaming.`);
            this.agentResponseCache.push({type, agentResponse, modality});  
            return;
        }

        this.server.log.debug(`Handling agent response of type ${type}: ${agentResponse}, modality: ${modality}`);

        if(type === 'Widget') {
            this.server.log.debug(`Received from Agent:${agentResponse}`);
            this.server.log.debug('Not sending to TTS');
            this.textResponse('agent', agentResponse, 'widget');
        } else {
            // send agentResponse to TTS if voice is enabled
            if (this.ttsWebSocket.readyState !== WebSocket.OPEN) {
                this.server.log.error('TTS WebSocket not open, reopening');
                await this.openTTSAndAwaitConnection();
            }
            this.server.log.debug(`Received from Agent:${agentResponse}`);
            this.textResponse('agent', agentResponse, 'audio');
            if(modality === 'audio') {
                this.server.log.debug(`Sending to TTS:${agentResponse}`);
                this.synthesizeText(agentResponse);
            }
        }
    }

    public appendText = async (message: string) => {
        this.chatHistory.push({ role: 'user', content: message });

        const chatJob = () => new Promise<void>((resolve, reject) => {
            const performJob = async () => {
                try {
                    await this.sendChatHistoryToAgent('text');
                    resolve();
                } catch(error) {
                    reject(error);
                }
            };
            performJob();
        });
        this.agentQueue.add(chatJob, () => {
            this.textResponse('agent', 'One moment please', 'text');
            this.synthesizeText('One moment please');
        });
    }

    public appendAudio = async (messageBuffer: Buffer): Promise<void> => {
        // this.server.log.debug("Received audio message");
        // append the binary message to the speech buffer

        // for deepgram, we can ignore VAD and send the audio directly
        if (STT_PROVIDER === 'deepgram') 
        {
            try { 
                // send the audio to the STT
                if(this.sttWebSocket.readyState !== WebSocket.OPEN) {
                    this.server.log.error('STT WebSocket not open, reopening');
                    await this.openSTTAndAwaitConnection();
                }
                this.sttWebSocket.send(messageBuffer);
            } catch(error) {
                this.server.log.error(`Error sending audio to STT: ${error}`);
            }
            // return; 
        }

        const audioTimeMs = (messageBuffer.length / SAMPLE_RATE / 2) * 1000;
        // do vad here?
        const res = await vad.processAudio(messageBuffer, SAMPLE_RATE);
        // handle the result of the VAD
        switch (res) {
            case VAD.Event.ERROR:
                // ignore noise if we havent received voice
                if(this.receivedVoice) {
                    // this.server.log.debug("appending error to voice");
                    this.speechBuffer = Buffer.concat([this.speechBuffer, messageBuffer]);
                    this.lastVoiceTime = new Date();
                    this.silenceDuration = 0;
                }
                break;
            case VAD.Event.NOISE:
                // ignore noise if we havent received voice
                if(this.receivedVoice) {
                    // this.server.log.debug("appending noise to voice");
                     this.speechBuffer = Buffer.concat([this.speechBuffer, messageBuffer]);
                    this.lastVoiceTime = new Date();
                    this.silenceDuration = 0;
                } 
                break;
            case VAD.Event.SILENCE:
                // this.server.log.debug("VAD Event SILENCE");
                // calculate silent time
                if(this.receivedVoice) {
                    // this.server.log.debug("appending silence to voice");
                    this.speechBuffer = Buffer.concat([this.speechBuffer, messageBuffer]);
                    this.lastVoiceTime = new Date();
                    this.silenceDuration += audioTimeMs;
                } else {
                    // this.server.log.debug("Silence detected but no voice received. Ignoring.");
                }
                break;
            case VAD.Event.VOICE:
                this.receivedVoice = true;
                this.speechBuffer = Buffer.concat([this.speechBuffer, messageBuffer]); 
                // this.server.log.debug("VAD Event VOICE");
                this.lastVoiceTime = new Date();
                this.silenceDuration = 0;
                if(this.speechBuffer.length > STT_WAIT_MS * SAMPLE_RATE * 2) {
                    this.server.log.debug("Speech detected");
                    await this.cancelAllAgentActivity();
                    this.speechBuffer = Buffer.alloc(0);
                }
                break;
        }
        // const timeSinceLastVoiceMs = new Date().getTime() - this.lastVoiceTime.getTime();
        // const speechDuration = (this.speechBuffer.length / SAMPLE_RATE / 2) * 1000;

        // determine whether we should send the text to STT
        if(res === VAD.Event.SILENCE && 
            this.silenceDuration > STT_WAIT_MS && 
            STT_PROVIDER !== 'deepgram'
        ) {
            await this.sendAudioBufferToSTT();
            this.silenceDuration = 0;
            this.speechBuffer = Buffer.alloc(0);
            this.lastVoiceTime = new Date();
            this.receivedVoice = false;
        }
    }

    sendAudioBufferToSTT = async (): Promise<void> => {
        this.server.log.debug(`---> Sending audio to STT`);
        if(this.sttWebSocket.readyState !== WebSocket.OPEN) {
            this.server.log.error(`STT WebSocket not open, reopening`);
            await this.openSTTAndAwaitConnection();
        }
        try {
            this.server.log.debug(`---> Sent audio to STT of size ${this.speechBuffer.length}`);
            this.sttWebSocket.send(this.speechBuffer);
        } catch(error) {
            this.server.log.error(`Error sending audio to STT: ${error}`);
        }
        this.speechBuffer = Buffer.alloc(0);
    }

    setAgentEnded = () => {
        this.waitingForAgent = false;
        this.textResponse('agent', 'agent_ended_thinking', 'action');
    }

    setAgentStarted = () => {
        this.waitingForAgent = true;
        this.textResponse('agent', 'agent_started_thinking', 'action');
    }

    appendChatHistory = (role: string, content: string): void => {
        this.chatHistory.push({ role, content });
    }

    // send chatHistory to openai's completion api and return the response async
    async sendChatHistoryToAgent(modality:string, action?: any): Promise<void> {
        this.setAgentStarted();
        const lastUserMessage = this.chatHistory.filter((message: ChatMessage) => message.role === 'user').pop();
        this.server.log.debug(`Sending to agent:${lastUserMessage?.content}`);

        this.server.log.debug(`send chat history to agent`);
        this.server.log.debug(`Sending to agent ${AGENT_HOST}:${AGENT_PORT}${AGENT_PATH}: ${JSON.stringify(this.chatHistory)}`);
        this.server.log.debug(`Sending to agent: ${JSON.stringify(this.sessionDict)}`);
    
        let body: {
            messages: ChatMessage[];
            session: { [key: string]: string };
            action?: any;
        } = {
            messages: this.chatHistory.slice(-MAX_AGENT_MESSAGES),
            session: this.sessionDict
        };

        if(action) {
            body.action = action;
        }

        const openAIResponse = await fetch(`http://${AGENT_HOST}:${AGENT_PORT}${AGENT_PATH}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream'
            },
            body: JSON.stringify(body)
        });

        // Store the task ID from the response headers in case you need to cancel it
        const taskId = openAIResponse.headers.get('X-Task-ID');
        if (taskId) {
            this.currentTaskId = taskId;
        }

        const reader = openAIResponse.body?.getReader();
        const decoder = new TextDecoder('utf-8');
        let done = false;
        let lastMessages = undefined;

        while (!done) {
            const { value, done: doneReading } = await reader?.read() || {};
            done = doneReading || false;
            if (value) {
                let responseText = decoder.decode(value, { stream: true });

                this.server.log.debug(`Raw output: ${responseText}`);
                const lines = responseText.split('\n');
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const jsonData = line.slice(6).trim();
                        if (jsonData) {
                            try {
                                const data = JSON.parse(jsonData);
                                this.server.log.debug(`Agent response: ${JSON.stringify(data)}`);

                                // If the guardrail validation failed, stop further processing
                                if (data.guardrails) {
                                    this.server.log.debug('Guardrails validation failed, stopping further processing.');
                                    this.setAgentEnded();
                                    const validatedOutput = data.guardrails[0]?.validated_output || "";
                                    await this.handleAgentResponse("CustomerResponse", "Sorry I am not going to respond to that. Try again but a bit nicer.", modality);
                                    break;
                                }

                                // Check for error in processing and provide something to the user
                                if (data.error) {
                                    await this.handleAgentResponse("CustomerResponse", "Sorry I had some trouble with that. Can you please repeat what you said?", modality);
                                    break;
                                }

                                // if the customer response node is present, send an audio response or a JSON object for a widget
                                lastMessages = data['messages'];
                                if(data.node === "CustomerResponse" || data.node === "TaskDescriptionResponse") {
                                    await this.handleAgentResponse("CustomerResponse", data.output, modality);
                                }
                                else if(data.node === "Widget") {
                                    await this.handleAgentResponse(data.node, data.output, modality);
                                }

                                this.sessionDict = data.session;
                            } catch (error) {
                                this.server.log.error(`Error parsing JSON: ${error}`);
                                this.server.log.error(jsonData);
                            }
                        } else {
                            this.server.log.error('Received empty data line');
                        }
                    }
                }
            }
        }
        
        // append last message to chatHistory
        if(lastMessages) {
            this.chatHistory = this.chatHistory.concat(lastMessages);
        }

        this.setAgentEnded();
    }

    async cancelAgentTask(taskId: string, lastMessages: ChatMessage[]): Promise<void> {
        
        this.server.log.error(`Cancellation request for ${taskId} received`);
        
        // log what the last message is at the time of cancellation
        this.server.log.error(`Current last messages at this time: ${JSON.stringify(lastMessages)}`);
        this.server.log.error(`Current last message role: ${lastMessages[lastMessages.length - 1].role}`);
        
        // Append last messages to chat history before cancellation if they are from the assistant
        if (lastMessages && lastMessages.length > 0 && lastMessages[lastMessages.length - 1].role === 'assistant') {
            this.chatHistory = this.chatHistory.concat(lastMessages);
        }

        // Make the post request to cancel the long running agent task
        try {
            const response = await fetch(`http://${AGENT_HOST}:${AGENT_PORT}${AGENT_CANCEL_PATH}/${taskId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) {
                this.server.log.error(`Failed to cancel task ${taskId}: ${response.statusText}`);
            } else {
                this.server.log.debug(`Successfully cancelled task ${taskId}`);
            }
        } catch (error) {
            this.server.log.error(`Error cancelling task ${taskId}: ${error}`);
        }
    }
}
