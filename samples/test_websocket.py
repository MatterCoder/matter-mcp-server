import argparse
import sys
import os
import asyncio
import logging
import coloredlogs
from pathlib import Path
import aiohttp
from aiorun import run
import time
from chip.clusters import Objects as clusters

path = "../python-matter-server"
sys.path.append(os.path.abspath(path))

from matter_server.client.client import MatterClient

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)


DEFAULT_VENDOR_ID = 0xFFF1
DEFAULT_FABRIC_ID = 1
DEFAULT_PORT = 5580
DEFAULT_URL = f"http://127.0.0.1:{DEFAULT_PORT}/ws"
DEFAULT_STORAGE_PATH = os.path.join(Path.home(), ".matter_server")

# Get parsed passed in arguments.
parser = argparse.ArgumentParser(description="Matter Client Example.")
parser.add_argument(
    "--storage-path",
    type=str,
    default=DEFAULT_STORAGE_PATH,
    help=f"Storage path to keep persistent data, defaults to {DEFAULT_STORAGE_PATH}",
)
parser.add_argument(
    "--port",
    type=int,
    default=DEFAULT_PORT,
    help=f"TCP Port on which to run the Matter WebSockets Server, defaults to {DEFAULT_PORT}",
)
parser.add_argument(
    "--log-level",
    type=str,
    default="info",
    help="Provide logging level. Example --log-level debug, default=info, possible=(critical, error, warning, info, debug)",
)

args = parser.parse_args()

if __name__ == "__main__":
    # configure logging
    logging.basicConfig(level=args.log_level.upper())
    coloredlogs.install(level=args.log_level.upper())

    async def run_matter():
        """Run the Matter client."""

        # run the client
        url = f"http://127.0.0.1:{args.port}/ws"
        async with aiohttp.ClientSession() as session:
            async with MatterClient(url, session) as client:
                # start listening
                await client.start_listening()

#        time.sleep(5)

    async def handle_stop(loop: asyncio.AbstractEventLoop):
        """Handle server stop."""
        #await server.stop()
        return

    # run the server
    run(run_matter(), shutdown_callback=handle_stop)

