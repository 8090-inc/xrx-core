import fastify, { FastifyInstance, FastifyRequest } from 'fastify';
import fastifyWebSocket from '@fastify/websocket'; // Import FastifySocketStream type
import WebSocket from 'ws'; // type structure for the websocket object used by fastify/websocket
import { Session } from './Session';
import 'dotenv/config'
import { configDotenv } from 'dotenv';
import { PassThrough } from 'stream';
import { WaveFile } from 'wavefile';

const installedffmpeg = require('@ffmpeg-installer/ffmpeg');
const ffmpeg = require('fluent-ffmpeg');
ffmpeg.setFfmpegPath(installedffmpeg.path);

configDotenv({ path: '../.env' });

// Import the Session class
// const WS_LOG_LEVEL = process.env['WS_LOG_LEVEL'] || 'debug';
const API_KEY = process.env['API_KEY'] || '123456';

const connectionMap = new Map<WebSocket, Session>();


// create fastify server (with logging enabled for non-PROD environments)
const server: FastifyInstance = fastify({
    logger: {
        level: 'debug',
        transport: {
            target: 'pino-pretty',
            options: {
                translateTime: 'HH:MM:ss Z',
                ignore: 'pid,hostname',
            },
        },
    },
});

// register the @fastify/websocket plugin with the fastify server
server.register(fastifyWebSocket);

server.addHook('preValidation', async (request, reply) => {
    server.log.debug('preValidation hook');
    // check if the request is authenticated
    /* if (request.headers['x-api-key'] !== API_KEY ) {
        await reply.code(401).send("not authenticated");
    }*/ 
})

server.register(async function (fastify) {

    // Route for Twilio to handle incoming calls
    // <Say> punctuation to improve text-to-speech translation
    fastify.get('/incoming-call', async (request, reply) => {
        const twimlResponse = `<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say>Welcome to xRx, by eighty ninety.</Say>
                <Pause length="1"/>
                <Say>State your intentions.</Say>
                <Connect>
                    <Stream url="ws://stage.cvmg.globex.dev/api/v1/ws" />
                </Connect>
            </Response>`;

        reply.type('text/xml').send(twimlResponse);
    });



    // create a websocket server
    fastify.get('/api/v1/ws', { websocket: true }, (socket:WebSocket, req: FastifyRequest ) => {
        
        // Handle new connection
        server.log.debug('Connection opened');
        server.log.debug(JSON.stringify(req.headers));

        let streamSid: string;

        // Create a new session and store it in the connection map
        const session = new Session(
            server,
            (audio:ArrayBuffer) => {
                const i16 = new Int16Array(audio);

                const wav = new WaveFile();
                wav.fromScratch(1, 24000, '16', i16);
                wav.toSampleRate(8000);
                wav.toMuLaw();
                const rawMuLawData = (wav.data as any).samples;

                // Split the buffer into 20ms chunks
                let chunkSize = 320; // For 8kHz µ-law audio, 20ms is 320 bytes

                for (let i = 0; i < rawMuLawData.length; i += chunkSize) {
                    let chunk = rawMuLawData.slice(i, i + chunkSize);
                    let base64Chunk = Buffer.from(chunk).toString("base64");

                    let message = {
                        event: "media",
                        streamSid: streamSid,
                        media: {
                            payload: base64Chunk,
                        },
                    };
      
                    socket.send(JSON.stringify(message));
                }

                // send audio to the client
                socket.send(audio);
            }, 
            (user:string, content:string, type:string) => {
                // send text to the client
                socket.send(JSON.stringify({user: user, content: content, type: type}));
            }
        );
        connectionMap.set(socket, session);

        const ffmpegInput = new PassThrough();
        const ffmpegCommand = ffmpeg(ffmpegInput)
            .inputOptions(['-f mulaw', '-ar 8000'])
            .outputFormat('s16le') // Set output format to s16le (16-bit PCM)
            .outputOptions(['-ar 16000']) // Set output sample rate to 16kHz
            .on('start', (cmd: string) => {
              console.log(`Starting ffmpeg with command: ${cmd}`);
            })
            .on('error', (err: {message: string}) => {
                console.error(`FFMPEG Error: ${err.message}`);
            })
            .on('end', () => {
                console.log('Conversion finished!');
            })
        const ffmpegOutput = ffmpegCommand.pipe();

        ffmpegOutput.on('data', (chunk: Buffer<ArrayBufferLike>) => {
            session.appendAudio(chunk);
        });

        socket.on('message', async (message, isBinary) => {
            if (isBinary) {
                return;
            }

            const data = JSON.parse(message as unknown as string);


            //const session = connectionMap.get(connection);
            if (!session) {
                server.log.error('Error: Session not found');
                return;
            }

            console.log("EVENT TYPE: " + data.event);

            if(data.event === "start") {
                streamSid = data.start.streamSid;
            } if(data.event === "media") {
                // THIS IS WHERE WE GET DATA FROM TWILIO
                
                // we received audio from the client, send to session
                const messageBuffer = Buffer.from(data.media.payload as unknown as string, "base64");
                ffmpegInput.write(messageBuffer);
            } else {
                // we received text from the client, send to session
                // const messageString = message.toString(); // convert Buffer to string
                // const messageObject = JSON.parse(messageString);
                // if (messageObject.type === 'text') {
                //     server.log.debug('Received text message:', messageString);
                //     await session.appendText(messageObject.content);
                // }
                // if (messageObject.type === 'action') {
                //     server.log.debug('Received action:', messageString);
                //     await session.cancelAllAgentActivity();
                //     await session.sendActionToAgent(messageObject.content.tool, messageObject.content.parameters, messageObject.modality);
                // }
            }
        });

        socket.on('close', (code, reason) => {
            // the client closed
            server.log.debug(`Connection closed: ${code} ${reason}`);
            session.close();
        });
    });
});

// start the server
const start = async () => {
    try {
        await server.listen({ port: 8000,host:'0.0.0.0' });
        server.log.debug('Server started on port 8000');
    } catch (err) {
        server.log.fatal(`Error starting server: ${(err as Error).message}`);
        process.exit(1);
    }
};

start();