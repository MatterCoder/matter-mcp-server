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
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

The `samples` directory contains various example scripts demonstrating different Matter protocol operations:

- Start listening for events: `python samples/Start_Listening.py`
- Commission devices: `python samples/Commission_with_Code.py`
- Get node information: `python samples/Get_Node.py`
- Send commands to devices: `python samples/Send_a_command.py`
- And more...

Each sample can be run directly after installing the dependencies.
