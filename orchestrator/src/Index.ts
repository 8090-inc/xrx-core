import fastify, { FastifyInstance, FastifyRequest } from 'fastify';
import fastifyWebSocket from '@fastify/websocket'; // Import FastifySocketStream type
import WebSocket from 'ws'; // type structure for the websocket object used by fastify/websocket
import { Session } from './Session';
import 'dotenv/config'
import { configDotenv } from 'dotenv';

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

    // create a websocket server
    fastify.get('/api/v1/ws', { websocket: true }, (socket:WebSocket, req: FastifyRequest ) => {
        
        // Handle new connection
        server.log.debug('Connection opened');
        server.log.debug(JSON.stringify(req.headers));

        // Create a new session and store it in the connection map
        const session = new Session(
            server,
            (audio:Buffer) => {
                // send audio to the client
                socket.send(audio);
            }, 
            (user:string, content:string, type:string) => {
                // send text to the client
                socket.send(JSON.stringify({user: user, content: content, type: type}));
            }
        );
        connectionMap.set(socket, session);

        socket.on('message', async (message, isBinary) => {
            //const session = connectionMap.get(connection);
            if (!session) {
                server.log.error('Error: Session not found');
                return;
            }

            if(isBinary) {
                // we received audio from the client, send to session
                //server.log.debug('Received binary message:', message);
                const messageBuffer = Buffer.from(message as Uint8Array);
                session.appendAudio(messageBuffer);
            } else {
                // we received text from the client, send to session
                const messageString = message.toString(); // convert Buffer to string
                const messageObject = JSON.parse(messageString);
                if (messageObject.type === 'text') {
                    server.log.debug('Received text message:', messageString);
                    await session.appendText(messageObject.content);
                }
                if (messageObject.type === 'action') {
                    server.log.debug('Received action:', messageString);
                    await session.cancelAllAgentActivity();
                    await session.sendActionToAgent(messageObject.content.tool, messageObject.content.parameters, messageObject.modality);
                }
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