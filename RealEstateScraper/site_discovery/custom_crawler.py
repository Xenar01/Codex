"""Custom crawler to return predefined sites from configuration."""

import os
import yaml


def custom_discover(keywords: list) -> list:
    """Read sites list from config.yaml and return their names and URLs."""
    cfg_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    cfg_path = os.path.abspath(cfg_path)
    with open(cfg_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    sites = config.get("sites", [])
    return [{"name": s.get("name", ""), "url": s.get("url", "")} for s in sites]

