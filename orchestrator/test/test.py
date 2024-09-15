import asyncio
import websockets
import pyaudio
import os
import simpleaudio as sa

# WebSocket server address
SERVER_ADDRESS = "ws://localhost:8000/api/v1/ws"
API_KEY = os.environ.get('API_KEY', '123456')

# PyAudio configuration
CHUNK_SIZE = 480  # 30ms of audio data at 16kHz sample rate
SAMPLE_RATE = 16000
CHANNELS = 1

p = pyaudio.PyAudio()

# Open a stream for audio input
stream = p.open(format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE)

play_obj = None
audio_buffer = []

async def start_audio_loop():
    headers = [("x-api-key", API_KEY)]

    async with websockets.connect(SERVER_ADDRESS, extra_headers=headers) as websocket:
        print("Connected to WebSocket server.")
        global playback_thread

        async def send_audio():
            print("Sending audio data...")
            try:
                while True:
                    # Read audio data from the microphone
                    data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                    byteData = bytearray(data)                     
                    await websocket.send(byteData)
                    # await websocket.send(b''.join(data))
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
                # if message is binary, play the audio, else print the message
                if isinstance(message, bytes):
                    print("Received audio")
                    audio_data = bytes(message)
                    audio_buffer.append(audio_data)
                else:
                    print(message)
                await asyncio.sleep(0)
        
        async def play_audio():
            global play_obj
            while True:
                if len(audio_buffer) > 0:
                    if play_obj is not None and play_obj.is_playing():
                        await asyncio.sleep(0)
                        continue
                    audio_data = audio_buffer.pop(0)
                    if(len(audio_data) > 0):
                        play_obj = sa.play_buffer(audio_data, 1, 2, SAMPLE_RATE)
                await asyncio.sleep(0)

        send_task = asyncio.create_task(send_audio())
        receive_task = asyncio.create_task(receive_messages())
        play_audio_task = asyncio.create_task(play_audio())
        # Run the send_audio and receive_messages tasks concurrently
        await asyncio.gather(send_task, receive_task, play_audio_task)

async def main():
    await start_audio_loop()

if __name__ == "__main__":
    asyncio.run(main())
