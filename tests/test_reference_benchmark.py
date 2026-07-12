from ragops.benchmarks import scenario_summary
from ragops.engine import evaluate
from ragops.loader import load_responses, load_scenario

SCENARIO = "scenarios/japanese_troubleshooting/benchmark-v0.2.json"
BASELINE = "scenarios/japanese_troubleshooting/benchmark-baseline.json"


def test_reference_benchmark_meets_published_taxonomy() -> None:
    summary = scenario_summary(load_scenario(SCENARIO))

    assert summary["case_count"] == 30
    assert len(summary["categories"]) == 9
    assert min(summary["categories"].values()) >= 3
    assert summary["languages"] == {"ja": 30}
    assert len(summary["attack_categories"]) >= 6


def test_reference_benchmark_baseline_passes() -> None:
    report = evaluate(load_scenario(SCENARIO), load_responses(BASELINE))

    assert report.passed is True
    assert report.metrics["citation_coverage"] == 1.0
    assert report.metrics["citation_precision"] == 1.0
    assert report.metrics["critical_findings"] == 0.0
