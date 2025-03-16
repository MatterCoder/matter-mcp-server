"""
DEVELOPER NOTE: Regularly run generate_datamodel.py to ensure the latest Matter 
datamodel definitions are present in device_types.py and clusters.py
"""

from typing import Any, List, Dict
import httpx
import xml.etree.ElementTree as ET
from mcp.server.fastmcp import FastMCP
import re
import json
import asyncio
from datamodel.device_types import device_types
from datamodel.clusters import clusters

# Initialize FastMCP server
mcp = FastMCP("matter-datamodel-mcp")

@mcp.tool()
async def get_device_type_id_from_name(device_name: str) -> int:
    """Get the device type Id from a device name
    
    Args:
        device_name: Name of the device type (e.g., 'Battery Storage', 'Cooktop')
    
    Returns:
        Device type Id as an integer
    """        
    for device_id, device_info in device_types.items():
        if device_info["label"].lower() == device_name.lower():
            return int(device_id)
    raise ValueError(f"Device type '{device_name}' not found")

@mcp.tool()
async def get_device_type_name_from_id(device_id: int) -> str:
    """Get the device type name from a device type Id
    
    Args:
        device_id: Device type Id (e.g., 24 for Battery Storage)
    
    Returns:
        Device type name as a string
    """
    device_id_str = str(device_id)
    if device_id_str in device_types:
        return device_types[device_id_str]["label"]
    raise ValueError(f"Device type Id {device_id} not found")

@mcp.tool()
async def get_cluster_id_from_name(cluster_name: str) -> int:
    """Get the cluster Id from a cluster name
    
    Args:
        cluster_name: Name of the cluster (e.g., 'Identify', 'Descriptor')
    
    Returns:
        Cluster Id as an integer
    """
    for cluster_id, cluster_info in clusters.items():
        if cluster_info["label"].lower() == cluster_name.lower():
            return int(cluster_id)
    raise ValueError(f"Cluster '{cluster_name}' not found")

@mcp.tool()
async def get_cluster_name_from_id(cluster_id: int) -> str:
    """Get the cluster name from a cluster Id
    
    Args:
        cluster_id: Cluster Id (e.g., 3 for Identify cluster)
    
    Returns:
        Cluster name as a string
    """
    cluster_id_str = str(cluster_id)
    if cluster_id_str in clusters:
        return clusters[cluster_id_str]["label"]
    raise ValueError(f"Cluster Id {cluster_id} not found")

@mcp.tool()
async def get_cluster_commands(cluster_identifier: str | int) -> List[str]:
    """Get a list of commands supported by a cluster
    
    Args:
        cluster_identifier: Either cluster name (e.g., 'DoorLock') or cluster ID (e.g., 257)
        
    Returns:
        List of command names supported by the cluster
        
    Raises:
        ValueError: If cluster cannot be found or XML cannot be parsed
    """
    # First, ensure we have the cluster name
    try:
        if isinstance(cluster_identifier, int) or cluster_identifier.isdigit():
            cluster_id = int(cluster_identifier)
            cluster_name = await get_cluster_name_from_id(cluster_id)
        else:
            cluster_name = cluster_identifier
            # Verify the cluster exists by trying to get its ID
            await get_cluster_id_from_name(cluster_name)
    except ValueError as e:
        raise ValueError(f"Invalid cluster identifier: {str(e)}")
    
    # Construct the GitHub raw URL for the XML file
    base_url = "https://raw.githubusercontent.com/project-chip/connectedhomeip/master/data_model/master/clusters"
    xml_url = f"{base_url}/{cluster_name}.xml"
    
    try:
        # Fetch the XML file
        async with httpx.AsyncClient() as client:
            response = await client.get(xml_url)
            if response.status_code != 200:
                raise ValueError(f"Failed to fetch cluster XML. Status code: {response.status_code}")
            
            # Parse the XML
            root = ET.fromstring(response.text)
            
            # Find all command elements and extract their names
            commands = []
            for command in root.findall(".//commands/command"):
                command_name = command.get('name')
                if command_name:
                    commands.append(command_name)
            
            if not commands:
                return ["No commands found for this cluster"]
                
            return commands
            
    except ET.ParseError:
        raise ValueError(f"Failed to parse XML for cluster {cluster_name}")
    except Exception as e:
        raise ValueError(f"Error fetching cluster commands: {str(e)}")

async def test_mappings():
    """Test function to verify the mapping tools"""
    try:
        print("\nTesting device type mappings:")
        device_name = "Battery Storage"
        device_id = await get_device_type_id_from_name(device_name)
        print(f"Device name '{device_name}' -> Id: {device_id}")
        name_back = await get_device_type_name_from_id(device_id)
        print(f"Device Id {device_id} -> name: '{name_back}'")
        
        print("\nTesting cluster mappings:")
        cluster_name = "Identify"
        cluster_id = await get_cluster_id_from_name(cluster_name)
        print(f"Cluster name '{cluster_name}' -> Id: {cluster_id}")
        name_back = await get_cluster_name_from_id(cluster_id)
        print(f"Cluster Id {cluster_id} -> name: '{name_back}'")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")

async def test_cluster_commands():
    """Test function to verify the cluster commands tool"""
    try:
        # Test with cluster name
        print("\nTesting cluster commands by name:")
        commands = await get_cluster_commands("DoorLock")
        print(f"DoorLock commands: {commands}")
        
        # Test with cluster ID
        print("\nTesting cluster commands by ID:")
        commands = await get_cluster_commands(257)  # 257 is DoorLock cluster ID
        print(f"Cluster 257 commands: {commands}")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    # For testing, uncomment this line:
    #asyncio.run(test_cluster_commands())
    
    # Run the MCP server
    mcp.run(transport='stdio')