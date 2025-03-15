import asyncio
import websockets
import json
import sys
import os
from pathlib import Path
import time

# Import the CHIP clusters
from chip.clusters import Objects as clusters

# Import the ability to turn objects into dictionaries, and vice-versa
from matter_server.common.helpers.util import dataclass_from_dict,dataclass_to_dict

async def produce(host: str, port: int, receive_timeout: float = 5.0):
    print(host)
    print(port)
    url = f"{host}:{port}/ws"

    command = clusters.DoorLock.Commands.UnlockDoor()
    payload = dataclass_to_dict(command)

    message = {
        "message_id": "device_command",
        "command": "device_command",
        "args": {
            "endpoint_id":  1,
            "node_id":  11,
            "payload": payload,
            "cluster_id": command.cluster_id,
            "command_name": "UnlockDoor",
            "timed_request_timeout_ms": 100,
            "interaction_timeout_ms":100,            
        }
    }

    async with websockets.connect(url) as ws:
        await ws.send(json.dumps(message))
        
        # Set end time for receiving messages
        end_time = time.time() + receive_timeout
        
        try:
            while time.time() < end_time:
                try:
                    # Set a timeout for each receive operation
                    return_message = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    print(f"Received: {return_message}")
                except asyncio.TimeoutError:
                    # No message received within 1 second, continue loop
                    continue
                
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")


if __name__ == "__main__":
    asyncio.run(produce(host='ws://127.0.0.1', port=5580))
