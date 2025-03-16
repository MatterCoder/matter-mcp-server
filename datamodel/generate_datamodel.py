import httpx
import asyncio
from pathlib import Path
import re
import json

async def download_descriptions():
    """Download the TypeScript descriptions file from GitHub"""
    url = "https://raw.githubusercontent.com/home-assistant-libs/python-matter-server/refs/heads/main/dashboard/src/client/models/descriptions.ts"
    
    datamodel_dir = Path(__file__).parent
    datamodel_dir.mkdir(exist_ok=True)
    output_file = datamodel_dir / "descriptions.ts"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch TypeScript descriptions. Status code: {response.status_code}")
        
        output_file.write_text(response.text)
        print(f"Successfully downloaded descriptions to {output_file}")

def load_descriptions() -> str:
    """Load the descriptions.ts file as a string"""
    descriptions_file = Path(__file__).parent / "descriptions.ts"
    return descriptions_file.read_text()

def extract_device_types(content: str) -> str:
    """Extract the device_types data between curly braces from the descriptions.ts content
    
    Args:
        content: The full content of descriptions.ts as a string
        
    Returns:
        The device_types data between curly braces
        
    Raises:
        ValueError: If device_types data cannot be found
    """
    pattern = r'export const device_types:\s*Record<number,\s*DeviceType>\s*=\s*({[\s\S]*?})\s*(?=export|$)'
    match = re.search(pattern, content)
    
    if not match:
        raise ValueError("Could not find device_types data in content")
        
    return match.group(1)

def add_variable_name(device_types_data: str) -> str:
    """Add 'device_types = ' to the start of the device types data
    
    Args:
        device_types_data: The device types data as a string
        
    Returns:
        The device types data with variable name prepended
    """
    return f"device_types = {device_types_data}"

def save_device_types() -> None:
    """Extract device types from descriptions.ts and save to device_types.py"""
    content = load_descriptions()
    device_types_data = extract_device_types(content)
    device_types_with_name = add_variable_name(device_types_data)
    
    output_file = Path(__file__).parent / "device_types.py"
    output_file.write_text(device_types_with_name)
    print(f"Successfully saved device types to {output_file}")

def extract_clusters(content: str) -> str:
    """Extract the clusters data between curly braces from the descriptions.ts content
    
    Args:
        content: The full content of descriptions.ts as a string
        
    Returns:
        The clusters data between curly braces
        
    Raises:
        ValueError: If clusters data cannot be found
    """
    pattern = r'export const clusters:\s*Record<number,\s*ClusterDescription>\s*=\s*({[\s\S]*?})\s*$'
    match = re.search(pattern, content)
    
    if not match:
        raise ValueError("Could not find clusters data in content")
        
    return match.group(1)

def add_clusters_variable_name(clusters_data: str) -> str:
    """Add 'clusters = ' to the start of the clusters data
    
    Args:
        clusters_data: The clusters data as a string
        
    Returns:
        The clusters data with variable name prepended
    """
    return f"clusters = {clusters_data}"

def save_clusters() -> None:
    """Extract clusters from descriptions.ts and save to clusters.py"""
    content = load_descriptions()
    clusters_data = extract_clusters(content)
    clusters_with_name = add_clusters_variable_name(clusters_data)
    
    output_file = Path(__file__).parent / "clusters.py"
    output_file.write_text(clusters_with_name)
    print(f"Successfully saved clusters to {output_file}")

if __name__ == "__main__":
    asyncio.run(download_descriptions())
    save_device_types()
    save_clusters()
