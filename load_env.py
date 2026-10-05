"""
Tiny .env file loader - no dependencies (no python-dotenv needed).

Reads a .env file in the project root (if it exists) and sets any
KEY=VALUE pairs found into os.environ, WITHOUT overwriting variables
that are already set in the real environment (so `set AZIZ_MODEL=x`
in your terminal still always wins over the .env file).

Usage (put this at the top of any entry-point script, before other
project imports that read os.environ):

    from load_env import load_env
    load_env()
"""
from __future__ import annotations

import os
from pathlib import Path


def load_env(path: str = ".env") -> dict:
    """
    Load KEY=VALUE lines from `path` into os.environ.
    Blank lines and lines starting with # are ignored.
    Returns a dict of what was actually loaded (for debugging/printing).
    """
    env_path = Path(path)
    loaded = {}
    if not env_path.exists():
        return loaded

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            continue
        # Real environment variables always win over .env file values.
        if key not in os.environ:
            os.environ[key] = value
        loaded[key] = value

    return loaded
