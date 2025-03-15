from typing import Any, Optional, Dict, List
from mcp.server.fastmcp import FastMCP
import asyncio
import websockets
import json
import time
from chip.clusters import Objects as clusters
from matter_server.common.helpers.util import dataclass_to_dict

# Initialize FastMCP server
mcp = FastMCP("matter-mcp-server")

async def send_websocket_command(message: Dict[str, Any], host: str = 'ws://127.0.0.1', 
                               port: int = 5580, receive_timeout: float = 2.0) -> List[Dict[str, Any]]:
    """Send command via WebSocket and receive response."""
    url = f"{host}:{port}/ws"
    responses = []
    
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps(message))
        end_time = time.time() + receive_timeout
        
        try:
            while time.time() < end_time:
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    responses.append(json.loads(response))
                except asyncio.TimeoutError:
                    continue
                
        except websockets.exceptions.ConnectionClosed:
            pass
    
    return responses

@mcp.tool()
async def get_nodes() -> List[Dict[str, int]]:
    """Get all commissioned nodes (returns only node IDs)."""
    message = {
        "message_id": "2",
        "command": "get_nodes"
    }
    response = await send_websocket_command(message)
    # Extract only node IDs from the response
    node_ids = []
    for item in response:
        if "result" in item:
            if isinstance(item["result"], list):
                # Handle case where result is a list of nodes
                for node in item["result"]:
                    if isinstance(node, dict) and "node_id" in node:
                        node_ids.append({"node_id": node["node_id"]})
            elif isinstance(item["result"], dict) and "node_id" in item["result"]:
                # Handle case where result is a single node
                node_ids.append({"node_id": item["result"]["node_id"]})
    return node_ids

@mcp.tool()
async def get_node(node_id: int) -> List[Dict[str, Any]]:
    """Get information about a specific node."""
    message = {
        "message_id": "2",
        "command": "get_node",
        "args": {
            "node_id": node_id
        }
    }
    return await send_websocket_command(message)

@mcp.tool()
async def start_listening() -> List[Dict[str, Any]]:
    """Start listening for node events and changes."""
    message = {
        "message_id": "3",
        "command": "start_listening"
    }
    return await send_websocket_command(message)

@mcp.tool()
async def set_wifi_credentials(ssid: str, credentials: str) -> List[Dict[str, Any]]:
    """Set WiFi credentials for device commissioning."""
    message = {
        "message_id": "1",
        "command": "set_wifi_credentials",
        "args": {
            "ssid": ssid,
            "credentials": credentials
        }
    }
    return await send_websocket_command(message)

@mcp.tool()
async def set_thread_dataset(dataset: str) -> List[Dict[str, Any]]:
    """Set Thread credentials for device commissioning."""
    message = {
        "message_id": "1",
        "command": "set_thread_dataset",
        "args": {
            "dataset": dataset
        }
    }
    return await send_websocket_command(message)

@mcp.tool()
async def commission_with_code(code: str, network_only: Optional[bool] = False) -> List[Dict[str, Any]]:
    """Commission a new device using QR code or manual pairing code."""
    message = {
        "message_id": "1",
        "command": "commission_with_code",
        "args": {
            "code": code
        }
    }
    if network_only:
        message["args"]["network_only"] = True
    return await send_websocket_command(message)


@mcp.tool()
async def read_attribute(node_id: int, attribute_path: str) -> List[Dict[str, Any]]:
    """Read an attribute from a node."""
    message = {
        "message_id": "read",
        "command": "read_attribute",
        "args": {
            "node_id": node_id,
            "attribute_path": attribute_path
        }
    }
    return await send_websocket_command(message)

@mcp.tool()
async def write_attribute(node_id: int, attribute_path: str, value: Any) -> List[Dict[str, Any]]:
    """Write an attribute value to a node."""
    # If the value is already a string, don't wrap it in extra quotes
    actual_value = value.strip('"') if isinstance(value, str) else value
    
    message = {
        "message_id": "write",
        "command": "write_attribute",
        "args": {
            "node_id": node_id,
            "attribute_path": attribute_path,
            "value": actual_value
        }
    }
    return await send_websocket_command(message)

@mcp.tool()
async def device_command(endpoint_id: int, node_id: int, cluster_id: int, 
                        command_name: str, payload: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
    """Send a command to a device.
    Args:
        endpoint_id: The endpoint ID of the device.
        node_id: The node ID of the device.
        cluster_id: The cluster ID of the command.
        command_name: The name of the command.
        payload: The payload of the command.
    """
    message = {
        "message_id": "device_command",
        "command": "device_command",
        "args": {
            "endpoint_id": endpoint_id,
            "node_id": node_id,
            "payload": payload,
            "cluster_id": cluster_id,
            "command_name": command_name,
            "timed_request_timeout_ms": 100,
            "interaction_timeout_ms":100,             
        }
    }
    return await send_websocket_command(message)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
