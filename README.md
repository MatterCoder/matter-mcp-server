
# matter-mcp-server
MCP Server for the Matter Devices

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


## Experimenting

The `samples` directory contains various example scripts demonstrating different Matter protocol operations:

- Start listening for events: `python samples/Start_Listening.py`
- Commission devices: `python samples/Commission_with_Code.py`
- Get node information: `python samples/Get_Node.py`
- Send commands to devices: `python samples/Send_a_command.py`
- And more...

Each sample can be run directly after installing the dependencies.
