import json
from dataclasses import replace

import pytest

from ragops.cli import main
from ragops.loader import ContractError
from ragops.stability import stability_markdown, stability_report
from ragops.statistical import replay_bundle_from_dict


def _bundle(values, *, scenario_id="scenario", metrics=("quality",)):
    """values: one list of repeats per case; each repeat is a float or a dict of metrics."""
    records = []
    for case_index, repeats in enumerate(values, start=1):
        for repeat_index, value in enumerate(repeats, start=1):
            metric_values = value if isinstance(value, dict) else {name: value for name in metrics}
            records.append({"case_id": f"case-{case_index}", "repeat_id": f"run-{repeat_index}", "metrics": metric_values})
    return replay_bundle_from_dict(
        {
            "schema_version": "0.1",
            "scenario_id": scenario_id,
            "scenario_digest": "sha256:s",
            "provenance": {k: k for k in ("dataset", "evidence", "evaluator", "application", "model", "model_config", "environment")},
            "records": records,
        }
    )


def test_stable_runs_pass_and_report_exact_numbers():
    report = stability_report(_bundle([[0.8, 0.8, 0.8], [0.5, 0.6, 0.7]]))
    item = report.metrics[0]
    assert report.decision == "PASS" and report.passed
    assert item.cases_measured == 2 and item.cases_with_single_run == 0
    assert item.mean_stddev == pytest.approx(0.05)  # (0 + 0.1) / 2
    assert item.max_range == pytest.approx(0.2)
    assert item.unstable_cases == () and item.unstable_fraction == 0.0
    assert report.failed_gates == ()


def test_range_boundary_is_exclusive_and_fraction_boundary_inclusive():
    cases = [[0.5, 0.5]] * 9 + [[0.2, 0.5]]                       # one case with range 0.3
    assert stability_report(_bundle(cases), max_range=0.3).decision == "PASS"          # 0.3 is not > 0.3
    at_limit = stability_report(_bundle(cases), max_range=0.2, max_unstable_fraction=0.1)
    assert at_limit.decision == "PASS" and at_limit.metrics[0].unstable_fraction == pytest.approx(0.1)
    over = stability_report(_bundle(cases), max_range=0.2, max_unstable_fraction=0.09)
    assert over.decision == "BLOCK" and over.failed_gates == ("unstable_fraction:quality",)
    assert over.metrics[0].unstable_cases == ("case-10",)


def test_flat_mean_but_flipping_cases_is_blocked():
    flipping = _bundle([[1.0, 0.0], [0.0, 1.0], [1.0, 0.0], [0.0, 1.0]])
    report = stability_report(flipping)
    assert report.decision == "BLOCK" and report.metrics[0].unstable_fraction == 1.0


def test_single_repeat_cases_are_skipped_but_counted():
    report = stability_report(_bundle([[0.5], [0.4, 0.4]]))
    assert report.metrics[0].cases_measured == 1 and report.metrics[0].cases_with_single_run == 1
    with pytest.raises(ContractError, match="no case with at least two repeats"):
        stability_report(_bundle([[0.5], [0.4]]))


def test_stddev_increase_against_a_baseline():
    base = _bundle([[0.5, 0.5], [0.5, 0.5]])
    candidate = _bundle([[0.5, 0.6], [0.5, 0.6]])       # stddev about 0.0707 per case
    ok = stability_report(candidate, baseline=base, max_stddev_increase=0.08, max_range=1.0)
    assert ok.decision == "PASS"
    assert ok.metrics[0].baseline_mean_stddev == 0.0 and ok.metrics[0].stddev_increase == pytest.approx(0.0707, abs=1e-3)
    bad = stability_report(candidate, baseline=base, max_stddev_increase=0.05, max_range=1.0)
    assert bad.decision == "BLOCK" and bad.failed_gates == ("stddev_increase:quality",)
    equal = stability_report(base, baseline=base, max_stddev_increase=0.0)
    assert equal.decision == "PASS"


def test_metric_selection_and_multiple_metrics():
    bundle = _bundle([[{"a": 0.1, "b": 0.0}, {"a": 0.1, "b": 1.0}]] * 2)
    both = stability_report(bundle)
    assert [m.metric for m in both.metrics] == ["a", "b"] and both.failed_gates == ("unstable_fraction:b",)
    only_a = stability_report(bundle, metrics=("a",))
    assert only_a.decision == "PASS" and [m.metric for m in only_a.metrics] == ["a"]
    with pytest.raises(ContractError, match="'missing'"):
        stability_report(bundle, metrics=("missing",))


@pytest.mark.parametrize(
    "kwargs,message",
    [
        ({"max_range": -1}, "max_range"),
        ({"max_range": float("nan")}, "max_range"),
        ({"max_range": True}, "max_range"),
        ({"max_unstable_fraction": -0.1}, "max_unstable_fraction"),
        ({"max_unstable_fraction": 1.5}, "at most 1"),
        ({"max_stddev_increase": 0.1}, "needs a baseline"),
    ],
)
def test_invalid_arguments(kwargs, message):
    with pytest.raises(ContractError, match=message):
        stability_report(_bundle([[0.5, 0.5]]), **kwargs)


def test_negative_increase_limit_and_scenario_mismatch_are_rejected():
    base = _bundle([[0.5, 0.5]])
    with pytest.raises(ContractError, match="max_stddev_increase"):
        stability_report(base, baseline=base, max_stddev_increase=-1)
    with pytest.raises(ContractError, match="different scenarios"):
        stability_report(base, baseline=_bundle([[0.5, 0.5]], scenario_id="other"))
    with pytest.raises(ContractError, match="no metrics"):
        stability_report(replace(base, records=()))
    single = _bundle([[0.5, 0.5]])
    with pytest.raises(ContractError, match="Baseline has no case"):
        stability_report(single, baseline=_bundle([[0.5], [0.5]]), max_stddev_increase=1)


def test_markdown_lists_unstable_cases_and_changes():
    cases = [[0.0, 1.0]] * 12
    candidate = _bundle(cases)
    text = stability_markdown(stability_report(candidate, baseline=_bundle([[0.5, 0.5]] * 12), max_stddev_increase=0.1))
    assert text.startswith("## RAGOps stability gate: BLOCK\n")
    assert "| `quality` | 12 | 0.7071 | 1 | 12 (100%) | BLOCK |" in text
    assert "mean stddev 0 -> 0.7071 (+0.7071)" in text and "(+2 more)" in text
    skipped = stability_markdown(stability_report(_bundle([[0.5], [0.4, 0.4]])))
    assert "1 case(s) skipped" in skipped and "PASS" in skipped


def test_stability_cli(tmp_path, monkeypatch, capsys):
    def write(name, bundle_values):
        path = tmp_path / name
        records = [
            {"case_id": f"c{i}", "repeat_id": f"r{j}", "metrics": {"quality": v}}
            for i, repeats in enumerate(bundle_values) for j, v in enumerate(repeats)
        ]
        path.write_text(json.dumps({
            "schema_version": "0.1", "scenario_id": "s", "scenario_digest": "sha256:s",
            "provenance": {k: k for k in ("dataset", "evidence", "evaluator", "application", "model", "model_config", "environment")},
            "records": records}), encoding="utf-8")
        return str(path)

    stable, flipping = write("stable.json", [[0.5, 0.5]] * 3), write("flip.json", [[0.0, 1.0]] * 3)
    monkeypatch.setattr("sys.argv", ["ragops", "stability", "--bundle", stable])
    assert main() == 0 and "stability gate: PASS" in capsys.readouterr().out
    out = tmp_path / "nested" / "report.json"
    monkeypatch.setattr("sys.argv", ["ragops", "stability", "--bundle", flipping, "--baseline-bundle", stable,
                                     "--max-stddev-increase", "0.1", "--metric", "quality", "--format", "json",
                                     "--output", str(out)])
    assert main() == 2
    assert json.loads(out.read_text())["failed_gates"] == ["unstable_fraction:quality", "stddev_increase:quality"]
    monkeypatch.setattr("sys.argv", ["ragops", "stability", "--bundle", str(tmp_path / "missing.json")])
    with pytest.raises(SystemExit, match="stability error"):
        main()


def test_bounds_defaults_and_counters():
    bundle = _bundle([[0.5, 0.5], [0.5]])
    assert stability_report(bundle, max_range=0, max_unstable_fraction=1).decision == "PASS"
    assert stability_report(bundle, max_unstable_fraction=0).decision == "PASS"
    two_single = stability_report(_bundle([[0.5, 0.5], [0.4], [0.3]]))
    assert two_single.metrics[0].cases_with_single_run == 2
    report = stability_report(bundle)
    assert (report.max_range, report.max_unstable_fraction, report.max_stddev_increase) == (0.2, 0.1, None)


def test_increase_is_candidate_minus_baseline():
    noisy = _bundle([[0.4, 0.6], [0.4, 0.6]])        # stddev ~0.1414
    calm = _bundle([[0.5, 0.52], [0.5, 0.52]])       # stddev ~0.01414
    item = stability_report(noisy, baseline=calm, max_stddev_increase=1.0, max_range=1.0).metrics[0]
    assert item.stddev_increase == pytest.approx(0.1414 - 0.01414, abs=1e-3)
    lower = stability_report(calm, baseline=noisy, max_stddev_increase=0.0, max_range=1.0)
    assert lower.metrics[0].stddev_increase < 0 and lower.decision == "PASS"
