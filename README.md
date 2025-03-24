
# matter-mcp-server

An MCP (Model-Context-Protocol) server that enables Claude and other AI assistants to directly interact with Matter devices and protocol operations. This server bridges the gap between AI language models and IoT device control by providing a structured interface for:

- Device commissioning and management
- Reading and writing device attributes
- Sending commands to Matter devices
- Monitoring device events and status
- Searching Matter protocol documentation
- Accessing Matter data models

By using matter-mcp-server, AI assistants can understand and control Matter devices through natural language, making complex IoT operations more accessible and intuitive. The server implements the FastMCP protocol, allowing seamless integration with Claude and other AI platforms that support MCP.

Key benefits:
- Direct AI control of Matter devices without complex coding
- Natural language interface for Matter protocol operations
- Real-time device monitoring and control
- Structured access to Matter documentation and data models

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/matter-mcp-server.git
cd matter-mcp-server
```

2. Create and activate a Python virtual environment:
```bash
python3 -m venv .venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Install uv (required for claude integration):

Use curl to download the script and execute it with sh. See this documentation: https://docs.astral.sh/uv/installation/

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If your system doesn't have curl, you can use wget:

```bash
wget -qO- https://astral.sh/uv/install.sh | sh
```

## Installing MCP in Claude

5. Edit the claude_desktop_config.json config file

This file is located in different locations depending on your operating system. e.g
Ubuntu: ~/.config/Claude
MacOS: ~/Library/Application Support/Claude
Windows: %APPDATA%\Claude

6. Add the following to claude_desktop_config.json:

```bash
{
    "mcpServers": {
        "matter-mcp-server": {
            "command": "uv",
            "args": [
                "--directory",
                "[REPLACE_WITH_FULL_PATH_TO_YOUR_REPO]",
                "run",
                "matter-mcp-server.py"
            ]
        }
    }
}
```

7. Restart Claude Desktop and wait for mcp tools to load

8. Claude Code - MCP Server install

If you have Claude Code installed then execute the following commands in a terminal

```bash
claude mcp add
```

```bash
mater-mcp-server
```

```bash
uv --directory [REPLACE_WITH_FULL_PATH_TO_YOUR_REPO] run matter-mcp-server.py
```

## Python Matter Server
The Python Matter Server is used by my MCP server. The Python Matter Server, from the Open Home Foundation, implements a Matter Controller Server over WebSockets using the official Matter (formerly CHIP) SDK.

For running the server and/or client in your development environment, see the [Development documentation](https://github.com/home-assistant-libs/python-matter-server/blob/main/DEVELOPMENT.md).

For running the Matter Server as a standalone docker container, see the  [docker instructions](https://github.com/home-assistant-libs/python-matter-server/blob/main/docs/docker.md).


## Testing with a Matter device?

A Matter Virtual Device (MVD) is a software-based emulator provided by Google that simulates Matter-compatible smart home devices for testing and development. It allows developers to validate device behavior without physical hardware. To set it up, use the Matter Virtual Device Tool, follow the steps in the [MVD official guide](https://developers.home.google.com/matter/tools/virtual-device)


## Experimenting

The `samples` directory contains various example scripts demonstrating different Matter protocol operations:

- Start listening for events: `python samples/Start_Listening.py`
- Commission devices: `python samples/Commission_with_Code.py`
- Get node information: `python samples/Get_Node.py`
- Send commands to devices: `python samples/Send_a_command.py`
- And more...

Each sample can be run directly after installing the dependencies.

## To give the agent more knowledge you can add these mcp servers:

```bash
{
    "mcpServers": {
        "matter-mcp-server": {
            "command": "uv",
            "args": [
                "--directory",
                "[REPLACE_WITH_FULL_PATH_TO_YOUR_REPO]",
                "run",
                "matter-mcp-server.py"
            ]
        },
        "matter-coder-search": {
            "command": "uv",
            "args": [
                "--directory",
                "[REPLACE_WITH_FULL_PATH_TO_YOUR_REPO]",
                "run",
                "matter-coder-search.py"
            ]
        },
        "matter-datamodel-mcp": {
            "command": "uv",
            "args": [
                "--directory",
                "[REPLACE_WITH_FULL_PATH_TO_YOUR_REPO]",
                "run",
                "matter-datamodel-mcp.py"
            ]
        }
    }    
}
```
