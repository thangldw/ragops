import json
from pathlib import Path

import pytest

from ragops.usage import UsageContractError, record_local_usage, summarize_local_usage


def _record(path: Path, **overrides) -> None:
    arguments = {
        "ragops_version": "2.0.2",
        "command": "demo",
        "exit_code": 0,
        "recorded_at": "2026-01-01T00:00:00Z",
    }
    arguments.update(overrides)
    record_local_usage(path, **arguments)


def test_record_and_summarize_round_trip(tmp_path: Path) -> None:
    log = tmp_path / "usage.jsonl"
    _record(log)
    _record(log, command="gate-v2", exit_code=1, recorded_at="2026-01-03T00:00:00Z")
    _record(log, recorded_at="2026-01-02T00:00:00Z")

    summary = summarize_local_usage(log)

    assert summary["event_count"] == 3
    assert summary["command_counts"] == {"demo": 2, "gate-v2": 1}
    assert summary["exit_code_counts"] == {"0": 2, "1": 1}
    assert summary["first_recorded_at"] == "2026-01-01T00:00:00Z"
    assert summary["last_recorded_at"] == "2026-01-03T00:00:00Z"


@pytest.mark.parametrize(
    "overrides",
    [
        {"command": "Bad Command"},
        {"command": "../etc/passwd"},
        {"exit_code": 256},
        {"exit_code": True},
        {"ragops_version": ""},
        {"recorded_at": "2026-01-01T00:00:00+01:00"},
        {"recorded_at": "not-a-time-Z"},
    ],
)
def test_invalid_events_are_refused_and_nothing_is_written(tmp_path: Path, overrides) -> None:
    log = tmp_path / "usage.jsonl"
    with pytest.raises(UsageContractError):
        _record(log, **overrides)
    assert not log.exists()


def _write(path: Path, *lines: str) -> Path:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_summary_rejects_malformed_files(tmp_path: Path) -> None:
    with pytest.raises(UsageContractError, match="readable"):
        summarize_local_usage(tmp_path / "missing.jsonl")
    with pytest.raises(UsageContractError, match="empty"):
        summarize_local_usage(_write(tmp_path / "empty.jsonl", "", "  "))
    with pytest.raises(UsageContractError, match="not valid JSON"):
        summarize_local_usage(_write(tmp_path / "bad.jsonl", "{nope"))
    with pytest.raises(UsageContractError, match="must be an object"):
        summarize_local_usage(_write(tmp_path / "list.jsonl", "[]"))


def test_summary_rejects_extra_or_missing_fields(tmp_path: Path) -> None:
    log = tmp_path / "usage.jsonl"
    _record(log)
    event = json.loads(log.read_text(encoding="utf-8"))

    with pytest.raises(UsageContractError, match="unexpected fields"):
        summarize_local_usage(_write(tmp_path / "a.jsonl", json.dumps({**event, "path": "/x"})))
    event.pop("command")
    with pytest.raises(UsageContractError, match="missing fields"):
        summarize_local_usage(_write(tmp_path / "b.jsonl", json.dumps(event)))
