"""Tests for envsnap.diff module."""

import pytest

from envsnap.diff import DiffResult, diff_dicts, diff_snapshots
from envsnap.snapshot import save


# ---------------------------------------------------------------------------
# DiffResult unit tests
# ---------------------------------------------------------------------------

def test_diff_result_is_empty_when_no_changes():
    result = DiffResult()
    assert result.is_empty


def test_diff_result_not_empty_with_added():
    result = DiffResult(added={"FOO": "bar"})
    assert not result.is_empty


def test_summary_no_differences():
    result = DiffResult()
    assert result.summary() == "(no differences)"


def test_summary_contains_added_prefix():
    result = DiffResult(added={"NEW_VAR": "hello"})
    assert result.summary().startswith("+")


def test_summary_contains_removed_prefix():
    result = DiffResult(removed={"OLD_VAR": "bye"})
    assert result.summary().startswith("-")


def test_summary_contains_changed_prefix():
    result = DiffResult(changed={"PORT": ("8000", "9000")})
    assert result.summary().startswith("~")


# ---------------------------------------------------------------------------
# diff_dicts tests
# ---------------------------------------------------------------------------

def test_diff_dicts_detects_added():
    env_a = {"HOME": "/root"}
    env_b = {"HOME": "/root", "DEBUG": "1"}
    result = diff_dicts(env_a, env_b)
    assert "DEBUG" in result.added
    assert result.added["DEBUG"] == "1"


def test_diff_dicts_detects_removed():
    env_a = {"HOME": "/root", "LEGACY": "old"}
    env_b = {"HOME": "/root"}
    result = diff_dicts(env_a, env_b)
    assert "LEGACY" in result.removed


def test_diff_dicts_detects_changed():
    env_a = {"PORT": "8000"}
    env_b = {"PORT": "9000"}
    result = diff_dicts(env_a, env_b)
    assert "PORT" in result.changed
    assert result.changed["PORT"] == ("8000", "9000")


def test_diff_dicts_identical_envs_is_empty():
    env = {"HOME": "/root", "USER": "alice"}
    result = diff_dicts(env, env)
    assert result.is_empty


# ---------------------------------------------------------------------------
# diff_snapshots integration test
# ---------------------------------------------------------------------------

def test_diff_snapshots_integration(tmp_path):
    snap_dir = str(tmp_path)
    env_a = {"APP": "envsnap", "ENV": "dev", "REMOVED": "gone"}
    env_b = {"APP": "envsnap", "ENV": "prod", "ADDED": "new"}

    save("snap_a", env_a, snapshot_dir=snap_dir)
    save("snap_b", env_b, snapshot_dir=snap_dir)

    result = diff_snapshots("snap_a", "snap_b", snapshot_dir=snap_dir)

    assert "ADDED" in result.added
    assert "REMOVED" in result.removed
    assert "ENV" in result.changed
    assert result.changed["ENV"] == ("dev", "prod")
    assert "APP" not in result.changed
