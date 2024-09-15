import asyncio
import websockets
import pyaudio
import json

# WebSocket server address
SERVER_ADDRESS = "ws://localhost:8002/api/v1/ws"

# PyAudio configuration
CHUNK_SIZE = 480
SAMPLE_RATE = 16000
CHANNELS = 1

async def start_loop():
    p = pyaudio.PyAudio()
    playback_stream = p.open(
        format=pyaudio.paInt16, channels=CHANNELS, rate=SAMPLE_RATE, output=True
    )

    audio_received = False
    synthesis_completed = False

    try:
        async with websockets.connect(SERVER_ADDRESS) as websocket:
            print("Connected to WebSocket server.")

            async def send_text():
                print("Sending text...")
                json_data = {
                    "action": "synthesize",
                    "text": "Hello, world, this is awesome!",
                }
                await websocket.send(json.dumps(json_data))

            async def receive_messages():
                nonlocal audio_received, synthesis_completed
                try:
                    async for message in websocket:
                        if isinstance(message, bytes):
                            print("Receiving audio...")
                            playback_stream.write(message)
                            audio_received = True
                        else:
                            data = json.loads(message)
                            if data.get("action") == "done":
                                print("Synthesis completed.")
                                synthesis_completed = True
                                break
                            else:
                                print(f"Received message: {message}")
                except websockets.exceptions.ConnectionClosed:
                    print("WebSocket connection closed unexpectedly")

            # Run the send_text and receive_messages tasks concurrently
            await asyncio.gather(send_text(), receive_messages())

    except websockets.exceptions.WebSocketException as e:
        print(f"WebSocket error: {e}")
        return False
    finally:
        playback_stream.stop_stream()
        playback_stream.close()
        p.terminate()

    # Check if both audio was received and synthesis completed
    if audio_received and synthesis_completed:
        print("Test PASSED: Audio received and synthesis completed successfully.")
        return True
    else:
        print("Test FAILED: Did not receive audio or synthesis did not complete.")
        return False

async def main():
    success = await start_loop()
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)