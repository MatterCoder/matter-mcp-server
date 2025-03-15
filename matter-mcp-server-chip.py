from typing import Any, Optional, Dict, List
from mcp.server.fastmcp import FastMCP
import asyncio
from asyncio import TimeoutError

# Initialize FastMCP server
mcp = FastMCP("matter-mcp-server")


async def run_chip_tool_command(*args: str, timeout: int = 30) -> str:
    """Execute a chip-tool command and return its output."""
    try:
        cmd = ["chip-tool"] + list(args)
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Add timeout to communicate
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )
        
        if process.returncode != 0:
            error_msg = stderr.decode().strip() if stderr else "Unknown error"
            raise Exception(f"chip-tool command failed: {error_msg}")
        
        return stdout.decode().strip()
    
    except TimeoutError:
        # Make sure to cleanup the process if it times out
        if process.returncode is None:
            process.kill()
            await process.wait()
        raise Exception(f"chip-tool command timed out after {timeout} seconds")
    except FileNotFoundError:
        raise Exception("chip-tool command not found. Please ensure it is installed and in your PATH")
    except Exception as e:
        raise Exception(f"Failed to execute chip-tool command: {str(e)}")

@mcp.tool()
async def commission_with_code(code: str | int) -> List[Dict[str, Any]]:
    """Commission a new device using QR code or manual pairing code.
    
    Args:
        code: The QR Code or Manual Pairing Code (can be string or integer)
    """
    try:
        node_id = "1"
        # Convert code to string if it's an integer
        code_str = str(code)
        result = await run_chip_tool_command("pairing", "onnetwork", node_id, code_str)
        
        return [{
            "status": "success",
            "message": result[0:200], # truncate the very long messages
            "node_id": node_id
        }]
    except Exception as e:
        return [{
            "status": "error",
            "message": str(e)
        }]

# Test function
async def test_commission():
    try:
        result = await commission_with_code("20202021")
        print("Commission result:", result)
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    # Run the test
    #asyncio.run(test_commission())
    
    # Alternatively, run as MCP server
    mcp.run(transport='stdio')













