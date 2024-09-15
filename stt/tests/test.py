import asyncio
import websockets
import pyaudio
import collections
import webrtcvad
import math

# WebSocket server address
SERVER_ADDRESS = "ws://localhost:8001/api/v1/ws"

# PyAudio configuration
CHUNK_SIZE = 480  # 30ms of audio data at 16kHz sample rate
SAMPLE_RATE = 16000
CHANNELS = 1

# WebRTCVAD configuration
VAD = webrtcvad.Vad()
VAD.set_mode(3)  # Set aggressiveness mode (0-3)
# PADDING_DURATION_MS = 300  # Duration of padding before and after speech
MAX_SILENCE_DURATION_MS = 250  # Maximum duration of silence before stopping the stream

async def send_audio_to_server():
    p = pyaudio.PyAudio()

    # Open a stream for audio input
    stream = p.open(format=pyaudio.paInt16,
                    channels=CHANNELS,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)

    async with websockets.connect(SERVER_ADDRESS) as websocket:

        print("Connected to WebSocket server.")
        async def send_audio():
            try:
                frames = collections.deque()
                is_speech_detected = False
                num_silence_chunks = 0

                while True:
                    # Read audio data from the microphone
                    data = stream.read(CHUNK_SIZE)

                    # Check if the frame contains speech
                    is_speech = VAD.is_speech(data, SAMPLE_RATE)

                    if is_speech:
                        is_speech_detected = True
                        frames.append(data)
                        num_silence_chunks = 0
                    elif is_speech_detected:
                        frames.append(data)
                        num_silence_chunks += 1
                        if num_silence_chunks > (MAX_SILENCE_DURATION_MS // 30):
                            print(f"Detected silence, sending {len(frames)} frames.")
                            # Send the audio data to the WebSocket server
                            await websocket.send(b''.join(frames))
                            frames.clear()
                            is_speech_detected = False
                            num_silence_chunks = 0
                    await asyncio.sleep(0)
            except KeyboardInterrupt:
                print("Stopping audio stream...")
            finally:
                # Clean up resources
                stream.stop_stream()
                stream.close()
                p.terminate()
          
        async def receive_messages():
            async for message in websocket:
                # Handle the received message here
                print(f"Received message: {message}")
                await asyncio.sleep(0)

        # Run the send_audio and receive_messages tasks concurrently
        await asyncio.gather(send_audio(), receive_messages())

async def main():
    await send_audio_to_server()

if __name__ == "__main__":
    asyncio.run(main())
