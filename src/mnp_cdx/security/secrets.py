"""Secret handling utilities for mnpCDX."""

from __future__ import annotations

import os


class SecretError(RuntimeError):
    pass


def require_secret(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SecretError(f"Missing required secret: {name}")
    return value
