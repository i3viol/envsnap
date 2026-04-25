"""Core snapshot module for capturing and storing environment variable snapshots."""

import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_SNAPSHOT_DIR = Path.home() / ".envsnap" / "snapshots"


def capture(context: str, exclude: Optional[list[str]] = None) -> dict:
    """Capture current environment variables into a snapshot dict."""
    exclude = exclude or []
    env_vars = {
        key: value
        for key, value in os.environ.items()
        if key not in exclude
    }
    timestamp = datetime.now(timezone.utc).isoformat()
    snapshot = {
        "context": context,
        "timestamp": timestamp,
        "env": env_vars,
        "checksum": _checksum(env_vars),
    }
    return snapshot


def save(snapshot: dict, snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> Path:
    """Persist a snapshot to disk as a JSON file."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    context = snapshot["context"]
    timestamp = snapshot["timestamp"].replace(":", "-").replace("+", "Z")
    filename = f"{context}_{timestamp}.json"
    filepath = snapshot_dir / filename
    filepath.write_text(json.dumps(snapshot, indent=2))
    return filepath


def load(filepath: Path) -> dict:
    """Load a snapshot from a JSON file."""
    if not filepath.exists():
        raise FileNotFoundError(f"Snapshot file not found: {filepath}")
    data = json.loads(filepath.read_text())
    if data.get("checksum") != _checksum(data.get("env", {})):
        raise ValueError(f"Checksum mismatch for snapshot: {filepath}")
    return data


def list_snapshots(context: Optional[str] = None, snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> list[Path]:
    """List available snapshot files, optionally filtered by context."""
    if not snapshot_dir.exists():
        return []
    pattern = f"{context}_*.json" if context else "*.json"
    return sorted(snapshot_dir.glob(pattern), reverse=True)


def _checksum(env_vars: dict) -> str:
    """Compute a stable SHA256 checksum of environment variable key-value pairs."""
    serialized = json.dumps(env_vars, sort_keys=True).encode()
    return hashlib.sha256(serialized).hexdigest()
