import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path("scripts").resolve()))

import grounding_labels as labels  # noqa: E402


def _filled(tmp_path: Path, name: str, *, flip: set[str] = frozenset()) -> Path:
    sheet = labels.export_sheet(name)
    truth = {item["id"]: item["label"] for item in labels.all_items()}
    for item in sheet["items"]:
        item["label"] = truth[item["id"]] ^ (item["id"] in flip)
    path = tmp_path / f"{name}.json"
    path.write_text(json.dumps(sheet), encoding="utf-8")
    return path


def test_exported_sheet_is_blind() -> None:
    sheet = labels.export_sheet("alice")
    assert all(item["label"] is None for item in sheet["items"])
    assert not any("kind" in item for item in sheet["items"])
    assert len(sheet["items"]) == len(labels.all_items())


def test_ingest_reports_agreement_and_disagreements(tmp_path: Path) -> None:
    flip = {labels.all_items()[0]["id"], labels.all_items()[1]["id"]}
    summary, calibration = labels.ingest(
        [str(_filled(tmp_path, "alice")), str(_filled(tmp_path, "bob", flip=flip))], "strict"
    )

    assert summary["reviewers"] == ["alice", "bob", "maintainer"]
    assert summary["disagreement_count"] == 2
    assert 0 < summary["reviewer_agreement_kappa"] < 1
    assert len(calibration["records"]) == summary["items"]
    assert {h["reviewer"] for h in calibration["records"][0]["human_labels"]} == {
        "alice", "bob", "maintainer"
    }


@pytest.mark.parametrize("mutation", ["missing", "bad_label", "unknown_id", "no_reviewer"])
def test_ingest_rejects_bad_sheets(tmp_path: Path, mutation: str) -> None:
    path = _filled(tmp_path, "alice")
    sheet = json.loads(path.read_text(encoding="utf-8"))
    if mutation == "missing":
        sheet["items"].pop()
    elif mutation == "bad_label":
        sheet["items"][0]["label"] = 2
    elif mutation == "unknown_id":
        sheet["items"][0]["id"] = "nope"
    else:
        sheet["reviewer"] = " "
    path.write_text(json.dumps(sheet), encoding="utf-8")
    with pytest.raises(labels.LabelError):
        labels.ingest([str(path)], "strict")


def test_duplicate_reviewer_name_is_rejected(tmp_path: Path) -> None:
    path = _filled(tmp_path, "maintainer")
    with pytest.raises(labels.LabelError, match="duplicate reviewer"):
        labels.ingest([str(path)], "strict")
