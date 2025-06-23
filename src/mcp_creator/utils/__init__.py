"""Utility functions and helpers."""

import re
from typing import Any


def validate_server_name(name: str) -> str:
    """
    Transform any string into a valid Python identifier.

    Args:
        name: Raw server name input

    Returns:
        Clean, valid Python identifier
    """
    # Remove special characters, keep alphanumeric and underscores
    clean = re.sub(r'[^a-zA-Z0-9_]', '_', name.strip())

    # Ensure it starts with a letter
    if clean and not clean[0].isalpha():
        clean = f"mcp_{clean}"

    # Handle empty strings
    if not clean:
        clean = "mcp_server"

    return clean.lower()


def format_status_message(
    success: bool,
    message: str,
    details: dict[str, Any] | None = None
) -> str:
    """
    Create consistent status messages with clear visual indicators.

    Args:
        success: Whether operation succeeded
        message: Main message text
        details: Optional additional details

    Returns:
        Formatted status message
    """
    icon = "✅" if success else "❌"
    result = f"{icon} {message}"

    if details:
        detail_lines = [f"  • {k}: {v}" for k, v in details.items()]
        result += "\n" + "\n".join(detail_lines)

    return result


def safe_filename(filename: str) -> str:
    """
    Create safe filename from arbitrary string.

    Args:
        filename: Raw filename input

    Returns:
        Safe filename suitable for filesystem use
    """
    # Replace problematic characters
    safe = re.sub(r'[<>:"/\\|?*]', '_', filename.strip())

    # Remove excessive underscores
    safe = re.sub(r'_+', '_', safe)

    # Trim underscores from ends
    safe = safe.strip('_')

    return safe or "untitled"


def merge_configs(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """
    Merge configuration dictionaries with intelligent overrides.

    Args:
        base: Base configuration
        override: Override values

    Returns:
        Merged configuration
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result
