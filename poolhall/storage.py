"""JSON persistence for the pool hall state."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def _atomic_write(path: Path, content: str) -> None:
    """Write content to ``path`` atomically through a temp file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


def save_json(path: Path, data: Any) -> None:
    """Serialize ``data`` to a JSON file safely."""
    _atomic_write(path, json.dumps(data, indent=2, ensure_ascii=False))


def load_json(path: Path, default: Any = None) -> Any:
    """Load a JSON file; return ``default`` when missing or broken."""
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError):
        return default


def read_text(path: Path) -> str | None:
    """Return file text, or None when the file is missing."""
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    """Write text content to a file atomically."""
    _atomic_write(path, content)
