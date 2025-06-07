"""Utilities for configuring and running VPN via OpenVPN CLI"""


import subprocess
from typing import Optional


_process: Optional[subprocess.Popen] = None


def connect(config_path: str):
    """Start OpenVPN using the given configuration file."""
    global _process
    _process = subprocess.Popen(["openvpn", "--config", config_path])
    return _process


def disconnect():
    """Terminate the running VPN process."""
    global _process
    if _process and _process.poll() is None:
        _process.terminate()
        _process.wait()
        _process = None

