"""Malformed calibration inputs must raise ContractError (found by mutation testing)."""

import json
from pathlib import Path

import pytest

from ragops.calibration import (
    CalibrationPolicy,
    CalibrationRecord,
    HumanLabel,
    calibrate_evaluator,
    load_calibration_set,
)
from ragops.loader import ContractError

POLICY = {
    "threshold": 0.5,
    "minimum_coverage": 0.0,
    "minimum_accuracy": 0.0,
    "maximum_mae": 1.0,
    "maximum_false_pass_rate": 1.0,
    "minimum_agreement": 0.0,
}


def _doc(**overrides):
    doc = {
        "schema_version": "1.0",
        "evaluator": "e",
        "policy": dict(POLICY),
        "records": [{"case_id": "a", "automated_score": 0.5, "human_labels": [{"reviewer": "r", "label": 1}]}],
    }
    doc.update(overrides)
    return doc


def _load(tmp_path: Path, doc) -> None:
    path = tmp_path / "set.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    load_calibration_set(path)


def test_a_valid_document_loads(tmp_path: Path) -> None:
    _load(tmp_path, _doc())
    path = tmp_path / "set.json"
    loaded = load_calibration_set(path)
    assert loaded.evaluator == "e" and loaded.records[0].human_labels[0].label == 1


def _record(**fields):
    base = {"case_id": "a", "automated_score": 0.5, "human_labels": [{"reviewer": "r", "label": 1}]}
    base.update(fields)
    return base


BAD_DOCS = {
    "top level is a list": [],
    "unsupported schema": _doc(schema_version="2.0"),
    "extra field": {**_doc(), "extra": 1},
    "empty evaluator": _doc(evaluator=""),
    "non-string evaluator": _doc(evaluator=3),
    "policy is a list": _doc(policy=[]),
    "policy missing a field": _doc(policy={k: v for k, v in POLICY.items() if k != "threshold"}),
    "policy value out of range": _doc(policy={**POLICY, "threshold": 2}),
    "policy value is bool": _doc(policy={**POLICY, "threshold": True}),
    "policy value is text": _doc(policy={**POLICY, "threshold": "x"}),
    "records is not a list": _doc(records={}),
    "records empty": _doc(records=[]),
    "record is a list": _doc(records=[[]]),
    "record has extra field": _doc(records=[_record(extra=1)]),
    "labels is not a list": _doc(records=[_record(human_labels={})]),
    "label is a list": _doc(records=[_record(human_labels=[[]])]),
    "label has extra field": _doc(records=[_record(human_labels=[{"reviewer": "r", "label": 1, "x": 1}])]),
    "label is 2": _doc(records=[_record(human_labels=[{"reviewer": "r", "label": 2}])]),
    "label is bool": _doc(records=[_record(human_labels=[{"reviewer": "r", "label": True}])]),
    "reviewer empty": _doc(records=[_record(human_labels=[{"reviewer": "", "label": 1}])]),
    "reviewer not text": _doc(records=[_record(human_labels=[{"reviewer": 5, "label": 1}])]),
    "duplicate reviewer": _doc(records=[_record(human_labels=[{"reviewer": "r", "label": 1}, {"reviewer": "r", "label": 0}])]),
    "case id empty": _doc(records=[_record(case_id="")]),
    "case id not text": _doc(records=[_record(case_id=4)]),
    "duplicate case id": _doc(records=[_record(), _record()]),
    "score above one": _doc(records=[_record(automated_score=1.5)]),
    "score is bool": _doc(records=[_record(automated_score=True)]),
    "score is text": _doc(records=[_record(automated_score="x")]),
}


@pytest.mark.parametrize("doc", list(BAD_DOCS.values()), ids=list(BAD_DOCS))
def test_malformed_documents_raise_contract_error(tmp_path: Path, doc) -> None:
    with pytest.raises(ContractError):
        _load(tmp_path, doc)


def test_unreadable_and_non_finite_files_raise_contract_error(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="Cannot load calibration set"):
        load_calibration_set(tmp_path / "missing.json")
    path = tmp_path / "nan.json"
    path.write_text('{"schema_version": "1.0", "x": NaN}', encoding="utf-8")
    with pytest.raises(ContractError, match="non-finite"):
        load_calibration_set(path)
    path.write_bytes(b"\xff\xfe")
    with pytest.raises(ContractError):
        load_calibration_set(path)


def test_unsupported_schema_message_names_the_version(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="Unsupported calibration set schema: 2.0"):
        _load(tmp_path, _doc(schema_version="2.0"))


def test_calibrate_evaluator_validates_direct_callers() -> None:
    policy = CalibrationPolicy(**POLICY)
    record = CalibrationRecord("a", 0.5, (HumanLabel("r", 1),))
    for evaluator, records in (("", (record,)), ("e", ()), ("e", (record, record))):
        with pytest.raises(ContractError):
            calibrate_evaluator(evaluator, records, policy)
    with pytest.raises(ContractError):
        calibrate_evaluator("e", (CalibrationRecord("", 0.5, ()),), policy)
