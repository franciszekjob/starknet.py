import socket
import subprocess
import time
from contextlib import closing
from pathlib import Path
from typing import Generator, List, Optional

import pytest

from starknet_py.tests.e2e.fixtures.constants import TESTNET_NETWORK_ADDRESS


def get_available_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("", 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.getsockname()[1]


def start_devnet(get_start_devnet_func, fork_mode: Optional[bool] = False):
    devnet_port = get_available_port()
    start_devnet_command = get_start_devnet_func(devnet_port, fork_mode=fork_mode)

    # pylint: disable=consider-using-with
    proc = subprocess.Popen(start_devnet_command)
    time.sleep(5)
    return devnet_port, proc


def get_start_devnet_command(
    devnet_port: int, fork_mode: Optional[bool] = False
) -> List[str]:
    devnet_path = Path(__file__).parent.parent / "devnet" / "bin" / "starknet-devnet"

    start_command = [
        str(devnet_path),
        "--port",
        str(devnet_port),
        "--accounts",  # deploys specified number of accounts
        str(1),
        "--seed",  # generates same accounts each time
        str(1),
        "--state-archive-capacity",
        "full",
    ]

    if fork_mode:
        start_command.extend(
            [
                "--fork-network",
                str(TESTNET_NETWORK_ADDRESS),
            ]
        )

    return start_command


@pytest.fixture(scope="package")
def devnet() -> Generator[str, None, None]:
    """
    Runs devnet instance once per module and returns it's address.
    """
    devnet_port, proc = start_devnet(get_start_devnet_command)
    yield f"http://localhost:{devnet_port}"
    proc.kill()


@pytest.fixture(scope="package")
def devnet_forking_mode() -> Generator[str, None, None]:
    """
    Runs devnet instance once per module and returns its address.
    """
    devnet_port, proc = start_devnet(get_start_devnet_command, fork_mode=True)
    yield f"http://localhost:{devnet_port}"
    proc.kill()
