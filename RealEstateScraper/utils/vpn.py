"""Utilities for configuring and running VPN via OpenVPN CLI"""
import subprocess


def connect(config_path: str):
    subprocess.run(["openvpn", "--config", config_path])
