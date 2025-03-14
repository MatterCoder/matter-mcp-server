import asyncio
import websockets
import json
import time

async def produce(message: str, host: str, port: int, receive_timeout: float = 5.0):
    print("Sending message:", message)
    print("Host:", host)
    print("Port:", port)
    url = f"{host}:{port}/ws"
    
    async with websockets.connect(url) as ws:
        await ws.send(message)
        
        # Set end time for receiving messages
        end_time = time.time() + receive_timeout
        
        try:
            while time.time() < end_time:
                try:
                    # Set a timeout for each receive operation
                    response = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    print(f"Received: {response}")
                except asyncio.TimeoutError:
                    # No message received within 1 second, continue loop
                    continue
                
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")


if __name__ == "__main__":
   
    messageObject = {
        "message_id": "1",
        "command": "set_wifi_credentials",
        "args": {
            "ssid": "wifi-name-here",
            "credentials": "wifi-password-here"
        }
    }
    asyncio.run(produce(
        message=json.dumps(messageObject), 
        host='ws://127.0.0.1', 
        port=5580,
        receive_timeout=5.0
    ))
