import asyncio
import websockets
import json
from json import JSONEncoder
import sys
import os
from pathlib import Path
import time

# Import the CHIP clusters
from chip.clusters import Objects as clusters
from chip.clusters import Types as types

path = "../python-matter-server"
sys.path.append(os.path.abspath(path))

# Import the ability to turn objects into dictionaries, and vice-versa
from matter_server.common.helpers.util import dataclass_from_dict,dataclass_to_dict, create_attribute_path, create_attribute_path_from_attribute

class MatterJsonEncoder(json.JSONEncoder):
    # pylint: disable=method-hidden
    def default(self, o):
        return o.__dict__ 

async def produce(host: str, port: int, receive_timeout: float = 5.0):
    print("Host:", host)
    print("Port:", port)
    url = f"{host}:{port}/ws"

    attribute_path = create_attribute_path_from_attribute(0, clusters.AccessControl.Attributes.Acl)

    acl = [ clusters.AccessControl.Structs.AccessControlEntryStruct(
        fabricIndex = 1,
        privilege = clusters.AccessControl.Enums.AccessControlEntryPrivilegeEnum.kAdminister,
        authMode = clusters.AccessControl.Enums.AccessControlEntryAuthModeEnum.kCase,
        subjects = [ 112233, 2 ],
        targets = [] ) 
    ]
    attributeAcl = clusters.AccessControl.Attributes.Acl( acl ) 

    payload = dataclass_to_dict(attributeAcl)

    message = {
        "message_id": "4",
        "command": "write_attribute",
        "args": {
            "endpoint_id":  0,
            "node_id":  1,
            "attribute_path": attribute_path,
            "value": payload['value']
        }
    }
    
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps(message, cls=MatterJsonEncoder))
        
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
    asyncio.run(produce(host='ws://127.0.0.1', port=5580, receive_timeout=5.0))
