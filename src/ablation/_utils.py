"""Shared utilities for the ablation package."""

from __future__ import annotations

import json
from typing import Any


def format_cli_value(value: Any) -> str:
    """Format a value for CLI argument passing (KEY=VALUE pairs)."""
    if isinstance(value, str):
        return value
    return json.dumps(value)
