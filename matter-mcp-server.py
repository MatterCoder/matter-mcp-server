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
async def get_nodes() -> List[Dict[str, Any]]:
    """Get all commissioned nodes, returning only the descriptor (29) and basic information (40) cluster attributes.
    
    Returns the original response structure but filters the attributes to only include:
    - Descriptor Cluster attributes (0/29/*)
    - Basic Information Cluster attributes (0/40/*)
    """
    message = {
        "message_id": "2",
        "command": "get_nodes"
    }
    response = await send_websocket_command(message)
    
    # Define the attribute patterns to keep
    keep_patterns = ["0/29/", "0/40/"]
    
    # Filter the response
    for item in response:
        if "result" in item:
            if isinstance(item["result"], list):
                for node in item["result"]:
                    if "attributes" in node:
                        # Create new attributes dict with only matching patterns
                        filtered_attrs = {
                            k: v for k, v in node["attributes"].items()
                            if any(pattern in k for pattern in keep_patterns)
                        }
                        node["attributes"] = filtered_attrs
            elif isinstance(item["result"], dict) and "attributes" in item["result"]:
                # Create new attributes dict with only matching patterns
                filtered_attrs = {
                    k: v for k, v in item["result"]["attributes"].items()
                    if any(pattern in k for pattern in keep_patterns)
                }
                item["result"]["attributes"] = filtered_attrs
    
    return response

@mcp.tool()
async def get_node(node_id: int, remove_patterns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Get essential information about a specific node.
    
    Args:
        node_id: The node ID to query
        remove_patterns: Optional list of attribute patterns to remove. Defaults to ["0/62/"]. Do not include in mcp tool call if you want to use the default.
        
    Returns:
        Original response structure with specified attribute patterns removed
    """
    message = {
        "message_id": "2",
        "command": "get_node",
        "args": {
            "node_id": node_id
        }
    }
    full_response = await send_websocket_command(message)
    
    # Use default pattern if none provided
    if remove_patterns is None:
        remove_patterns = ["0/62/"]
    
    # Filter the response
    for item in full_response:
        if "result" in item:
            node_data = item["result"]
            if "attributes" in node_data:
                # Keep attributes that don't match any of the remove patterns
                filtered_attrs = {
                    k: v for k, v in node_data["attributes"].items()
                    if not any(pattern in k for pattern in remove_patterns)
                }
                node_data["attributes"] = filtered_attrs
    
    return full_response

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

async def test_get_nodes():
    print(await get_node(13))

if __name__ == "__main__":
    #asyncio.run(test_get_nodes()) # uncomment to run test
    #     
    # Initialize and run the server
    mcp.run(transport='stdio')
