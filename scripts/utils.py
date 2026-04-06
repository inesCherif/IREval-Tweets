"""
utils.py — Shared helpers: logging, file loading, config reading.
"""

import logging
import os
import yaml
from dotenv import load_dotenv

load_dotenv()


def get_logger(name: str) -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger(name)


def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_x_credentials() -> tuple[str, str]:
    """Read X session cookies from environment."""
    auth_token = os.getenv("X_AUTH_TOKEN")
    ct0 = os.getenv("X_CT0")
    if not auth_token or not ct0:
        raise EnvironmentError(
            "X_AUTH_TOKEN or X_CT0 not set. "
            "Please extract these cookies from your logged-in X.com session "
            "and put them in your .env file."
        )
    return auth_token, ct0


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)