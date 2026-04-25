"""envsnap — Capture, diff, and restore environment variable snapshots."""

__version__ = "0.1.0"
__author__ = "envsnap contributors"

from envsnap.snapshot import capture, save, load, list_snapshots

__all__ = ["capture", "save", "load", "list_snapshots"]
