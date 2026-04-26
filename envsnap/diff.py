"""Diff two environment snapshots and report added, removed, and changed variables."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envsnap.snapshot import load


@dataclass
class DiffResult:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)

    @property
    def is_empty(self) -> bool:
        return not (self.added or self.removed or self.changed)

    def summary(self) -> str:
        lines: List[str] = []
        for key, value in sorted(self.added.items()):
            lines.append(f"+ {key}={value}")
        for key, value in sorted(self.removed.items()):
            lines.append(f"- {key}={value}")
        for key, (old, new) in sorted(self.changed.items()):
            lines.append(f"~ {key}: {old!r} -> {new!r}")
        return "\n".join(lines) if lines else "(no differences)"


def diff_snapshots(
    name_a: str,
    name_b: str,
    snapshot_dir: Optional[str] = None,
) -> DiffResult:
    """Load two named snapshots and return a DiffResult describing their differences."""
    kwargs = {"snapshot_dir": snapshot_dir} if snapshot_dir else {}
    env_a = load(name_a, **kwargs)
    env_b = load(name_b, **kwargs)
    return diff_dicts(env_a, env_b)


def diff_dicts(env_a: Dict[str, str], env_b: Dict[str, str]) -> DiffResult:
    """Compare two environment dictionaries and return a DiffResult."""
    result = DiffResult()

    keys_a = set(env_a)
    keys_b = set(env_b)

    for key in keys_b - keys_a:
        result.added[key] = env_b[key]

    for key in keys_a - keys_b:
        result.removed[key] = env_a[key]

    for key in keys_a & keys_b:
        if env_a[key] != env_b[key]:
            result.changed[key] = (env_a[key], env_b[key])

    return result
