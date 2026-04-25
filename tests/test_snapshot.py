"""Tests for the envsnap snapshot module."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from envsnap.snapshot import capture, save, load, list_snapshots, _checksum


SAMPLE_ENV = {"HOME": "/home/user", "PATH": "/usr/bin", "SECRET": "abc123"}


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    return tmp_path / "snapshots"


def test_capture_returns_expected_keys():
    with patch.dict("os.environ", SAMPLE_ENV, clear=True):
        snap = capture("dev")
    assert snap["context"] == "dev"
    assert "timestamp" in snap
    assert "env" in snap
    assert "checksum" in snap


def test_capture_excludes_keys():
    with patch.dict("os.environ", SAMPLE_ENV, clear=True):
        snap = capture("dev", exclude=["SECRET"])
    assert "SECRET" not in snap["env"]
    assert "HOME" in snap["env"]


def test_checksum_is_deterministic():
    c1 = _checksum({"A": "1", "B": "2"})
    c2 = _checksum({"B": "2", "A": "1"})
    assert c1 == c2


def test_save_creates_file(tmp_snapshot_dir):
    with patch.dict("os.environ", SAMPLE_ENV, clear=True):
        snap = capture("staging")
    filepath = save(snap, snapshot_dir=tmp_snapshot_dir)
    assert filepath.exists()
    assert filepath.suffix == ".json"
    assert "staging" in filepath.name


def test_load_roundtrip(tmp_snapshot_dir):
    with patch.dict("os.environ", SAMPLE_ENV, clear=True):
        snap = capture("prod")
    filepath = save(snap, snapshot_dir=tmp_snapshot_dir)
    loaded = load(filepath)
    assert loaded["context"] == "prod"
    assert loaded["env"] == snap["env"]


def test_load_raises_on_missing_file(tmp_snapshot_dir):
    with pytest.raises(FileNotFoundError):
        load(tmp_snapshot_dir / "nonexistent.json")


def test_load_raises_on_tampered_checksum(tmp_snapshot_dir):
    with patch.dict("os.environ", SAMPLE_ENV, clear=True):
        snap = capture("dev")
    filepath = save(snap, snapshot_dir=tmp_snapshot_dir)
    data = json.loads(filepath.read_text())
    data["env"]["INJECTED"] = "evil"
    filepath.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="Checksum mismatch"):
        load(filepath)


def test_list_snapshots_filters_by_context(tmp_snapshot_dir):
    for ctx in ["dev", "dev", "prod"]:
        with patch.dict("os.environ", SAMPLE_ENV, clear=True):
            snap = capture(ctx)
        save(snap, snapshot_dir=tmp_snapshot_dir)
    dev_snaps = list_snapshots("dev", snapshot_dir=tmp_snapshot_dir)
    assert len(dev_snaps) == 2
    assert all("dev" in p.name for p in dev_snaps)


def test_list_snapshots_empty_dir(tmp_snapshot_dir):
    result = list_snapshots(snapshot_dir=tmp_snapshot_dir)
    assert result == []
