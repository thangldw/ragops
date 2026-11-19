import json

import pytest

from ragops.calibration import (
    CalibrationPolicy,
    CalibrationRecord,
    HumanLabel,
    calibrate_evaluator,
    confident_band,
)
from ragops.cli import main
from ragops.loader import ContractError
from ragops.triage import load_band, load_evaluation_scores, triage_cases, triage_markdown


def _policy(threshold=0.5):
    return CalibrationPolicy(threshold, 0.0, 0.0, 1.0, 1.0, 0.0)


def _rec(case_id, score, label):
    return CalibrationRecord(case_id, score, (HumanLabel("r", label),))


def _labeled():
    # clear cases agree with humans; the middle (0.4-0.6) is noise
    return (
        _rec("a", 0.95, 1), _rec("b", 0.9, 1), _rec("c", 0.85, 1), _rec("d", 0.05, 0), _rec("e", 0.1, 0), _rec("f", 0.15, 0),
        _rec("g", 0.6, 0), _rec("h", 0.55, 1), _rec("i", 0.45, 1), _rec("j", 0.4, 0),
    )


def test_band_excludes_the_noisy_middle():
    band = confident_band(_labeled(), _policy(), 1.0, minimum_decided=5)
    assert band is not None
    assert band.threshold == 0.5 and band.margin == pytest.approx(0.35)
    assert (band.lower, band.upper) == (pytest.approx(0.15), pytest.approx(0.85))
    assert band.accuracy == 1.0 and band.decided_cases == 6 and band.coverage == pytest.approx(0.6)
    assert band.target_accuracy == 1.0


def test_lower_targets_decide_more_and_unreachable_targets_give_none():
    loose = confident_band(_labeled(), _policy(), 0.7, minimum_decided=5)
    assert loose is not None and loose.decided_cases >= 6 and loose.accuracy >= 0.7
    assert confident_band(_labeled(), _policy(), 1.0, minimum_decided=7) is None  # too few remain
    noisy = (_rec("a", 0.9, 0), _rec("b", 0.1, 1), _rec("c", 0.8, 0), _rec("d", 0.2, 1), _rec("e", 0.7, 0))
    assert confident_band(noisy, _policy(), 0.9, minimum_decided=1) is None
    assert confident_band((), _policy(), 0.9) is None
    assert confident_band(_labeled(), _policy(), 0.9, minimum_decided=0) is None


def test_margin_zero_means_everything_is_decided_when_the_evaluator_is_accurate():
    perfect = (_rec("a", 0.9, 1), _rec("b", 0.1, 0), _rec("c", 0.5, 1), _rec("d", 0.8, 1), _rec("e", 0.2, 0))
    band = confident_band(perfect, _policy(), 1.0, minimum_decided=5)
    assert band is not None and band.margin == 0.0 and band.coverage == 1.0 and (band.lower, band.upper) == (0.5, 0.5)


def test_band_is_clipped_to_the_unit_interval():
    records = (_rec("a", 0.99, 1), _rec("b", 0.98, 1), _rec("c", 0.97, 1), _rec("d", 0.96, 1), _rec("e", 0.95, 1), _rec("f", 0.6, 0))
    band = confident_band(records, _policy(0.9), 1.0, minimum_decided=5)
    assert band is not None and band.upper <= 1.0 and band.lower >= 0.0


def test_calibrate_reports_the_band_only_when_asked():
    assert calibrate_evaluator("e", _labeled(), _policy()).confidence_band is None
    report = calibrate_evaluator("e", _labeled(), _policy(), target_accuracy=1.0)
    assert report.confidence_band is not None and report.to_dict()["confidence_band"]["decided_cases"] == 6
    with pytest.raises(ContractError, match="target accuracy"):
        calibrate_evaluator("e", _labeled(), _policy(), target_accuracy=2.0)


def test_triage_routes_by_margin_and_decides_the_boundary_case():
    band = confident_band(_labeled(), _policy(), 1.0, minimum_decided=5)
    routed = triage_cases({"hi": 0.9, "edge-hi": 0.85, "mid": 0.5, "edge-lo": 0.15, "lo": 0.05, "near": 0.7}, band, "m")
    by_id = {case.case_id: case.route for case in routed.cases}
    assert by_id == {"hi": "auto-pass", "edge-hi": "auto-pass", "mid": "needs-review",
                     "edge-lo": "auto-fail", "lo": "auto-fail", "near": "needs-review"}
    assert routed.counts() == {"auto-pass": 2, "auto-fail": 2, "needs-review": 2}
    assert routed.decided_share == pytest.approx(4 / 6)
    with pytest.raises(ContractError):
        triage_cases({}, band, "m")


def test_triage_with_a_clipped_band_still_uses_the_real_margin():
    records = tuple(_rec(f"low{i}", 0.5 + i * 0.02, 0) for i in range(5)) + (
        _rec("n1", 0.85, 1), _rec("n2", 0.95, 0), _rec("n3", 1.0, 0),
    )
    band = confident_band(records, _policy(0.9), 1.0, minimum_decided=5)
    assert band is not None and band.margin == pytest.approx(0.32) and band.upper == 1.0
    routed = {case.case_id: case.route for case in triage_cases({"top": 1.0, "far": 0.3, "mid": 0.75}, band, "m").cases}
    assert routed == {"top": "needs-review", "far": "auto-fail", "mid": "needs-review"}


def test_markdown_lists_the_review_queue_and_escapes_names():
    band = confident_band(_labeled(), _policy(), 1.0, minimum_decided=5)
    text = triage_markdown(triage_cases({"a|b`c": 0.5, "ok": 0.95}, band, "lexical_groundedness"))
    assert text.startswith("## RAGOps triage on `lexical_groundedness`")
    assert "- auto-pass: 1" in text and "- needs-review: 1 (50%)" in text
    assert "| `a\\|b\\`c` | 0.5 |" in text and "100%" in text
    clean = triage_markdown(triage_cases({"ok": 0.95}, band, "m"))
    assert "Needs review" not in clean


def _write(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


def test_loaders_validate_their_inputs(tmp_path):
    with pytest.raises(ContractError, match="no confidence band"):
        load_band(_write(tmp_path / "c.json", {"decision": "PASS", "confidence_band": None}))
    with pytest.raises(ContractError, match="no confidence band"):
        load_band(_write(tmp_path / "c.json", []))
    with pytest.raises(ContractError, match="Invalid confidence band"):
        load_band(_write(tmp_path / "c.json", {"confidence_band": {"threshold": 0.5}}))
    with pytest.raises(ContractError, match="Cannot read calibration report"):
        load_band(tmp_path / "missing.json")
    (tmp_path / "nan.json").write_text('{"x": NaN}', encoding="utf-8")
    with pytest.raises(ContractError, match="non-finite"):
        load_evaluation_scores(tmp_path / "nan.json", "m")
    good = {"cases": [{"case_id": "a", "m": 0.5}, {"case_id": "b", "m": 1}]}
    assert load_evaluation_scores(_write(tmp_path / "e.json", good), "m") == {"a": 0.5, "b": 1.0}
    for bad, message in (
        ({"cases": []}, "no cases"), ([], "no cases"), ({"cases": [3]}, "no case_id"),
        ({"cases": [{"case_id": 1, "m": 1}]}, "no case_id"),
        ({"cases": [{"case_id": "a"}]}, "numeric 'm'"), ({"cases": [{"case_id": "a", "m": True}]}, "numeric"),
        ({"cases": [{"case_id": "a", "m": "x"}]}, "numeric"),
        ({"cases": [{"case_id": "a", "m": 1}, {"case_id": "a", "m": 1}]}, "Duplicate"),
    ):
        with pytest.raises(ContractError, match=message):
            load_evaluation_scores(_write(tmp_path / "bad.json", bad), "m")


def test_calibrate_and_triage_cli(tmp_path, monkeypatch, capsys):
    records = [{"case_id": r.case_id, "automated_score": r.automated_score,
                "human_labels": [{"reviewer": "r", "label": r.human_labels[0].label}]} for r in _labeled()]
    cal = _write(tmp_path / "set.json", {
        "schema_version": "1.0", "evaluator": "lex", "records": records,
        "policy": {"threshold": 0.5, "minimum_coverage": 0.0, "minimum_accuracy": 0.0, "maximum_mae": 1.0,
                   "maximum_false_pass_rate": 1.0, "minimum_agreement": 0.0}})
    out = tmp_path / "report.json"
    monkeypatch.setattr("sys.argv", ["ragops", "calibrate", "--input", cal, "--output", str(out), "--target-accuracy", "1.0"])
    assert main() == 0
    capsys.readouterr()
    assert json.loads(out.read_text())["confidence_band"]["decided_cases"] == 6
    evaluation = _write(tmp_path / "eval.json", {"cases": [{"case_id": "a", "lexical_groundedness": 0.9},
                                                           {"case_id": "b", "lexical_groundedness": 0.5}]})
    monkeypatch.setattr("sys.argv", ["ragops", "triage", "--evaluation", evaluation, "--calibration", str(out)])
    assert main() == 0 and "needs-review: 1" in capsys.readouterr().out
    dest = tmp_path / "nested" / "triage.json"
    monkeypatch.setattr("sys.argv", ["ragops", "triage", "--evaluation", evaluation, "--calibration", str(out),
                                     "--format", "json", "--output", str(dest)])
    assert main() == 0 and json.loads(dest.read_text())["counts"]["auto-pass"] == 1
    monkeypatch.setattr("sys.argv", ["ragops", "triage", "--evaluation", evaluation, "--calibration", str(tmp_path / "x.json")])
    with pytest.raises(SystemExit, match="triage error"):
        main()
    # a calibration report without a band (target unreachable) is a clear error
    monkeypatch.setattr("sys.argv", ["ragops", "calibrate", "--input", cal, "--output", str(out), "--target-accuracy", "1.0", "--minimum-decided", "99"])
    main()
    capsys.readouterr()
    monkeypatch.setattr("sys.argv", ["ragops", "triage", "--evaluation", evaluation, "--calibration", str(out)])
    with pytest.raises(SystemExit, match="no confidence band"):
        main()


def test_a_score_exactly_on_the_threshold_with_no_margin_passes():
    band = confident_band((_rec("a", 0.9, 1), _rec("b", 0.1, 0), _rec("c", 0.5, 1), _rec("d", 0.8, 1), _rec("e", 0.2, 0)),
                          _policy(), 1.0, minimum_decided=5)
    assert band is not None and band.margin == 0.0
    routed = {c.case_id: c.route for c in triage_cases({"on": 0.5, "above": 0.51, "below": 0.49}, band, "m").cases}
    assert routed == {"on": "auto-pass", "above": "auto-pass", "below": "auto-fail"}
