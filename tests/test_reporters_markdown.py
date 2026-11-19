from ragops.drift import detect_evaluator_drift
from ragops.reporters import evaluator_drift_markdown, sequential_comparison_markdown
from ragops.sequential import compare_replay_bundles_sequentially
from tests import test_evaluator_drift as drift_fixtures
from tests import test_sequential_gate as sequential_fixtures


def test_evaluator_drift_markdown_reports_pass_and_block() -> None:
    passing = detect_evaluator_drift(
        drift_fixtures._bundle(0.95, "judge-v1"),
        drift_fixtures._bundle(0.96, "judge-v2"),
        drift_fixtures._policy(),
    )
    blocking = detect_evaluator_drift(
        drift_fixtures._bundle(0.95, "judge-v1"),
        drift_fixtures._bundle(0.90, "judge-v2"),
        drift_fixtures._policy(),
    )

    ok = evaluator_drift_markdown(passing)
    bad = evaluator_drift_markdown(blocking)

    assert "evaluator drift check: PASS" in ok and "None." in ok
    assert "evaluator drift check: BLOCK" in bad
    assert "`evaluator_drift:citation_precision`" in bad
    assert "citation_precision" in bad and "judge-v2" in bad


def test_sequential_markdown_covers_decided_and_undecided_runs() -> None:
    decided = compare_replay_bundles_sequentially(
        sequential_fixtures._bundle(0.95, "baseline", 4),
        sequential_fixtures._bundle(0.95, "candidate", 4),
        sequential_fixtures._policy(),
    )
    undecided = compare_replay_bundles_sequentially(
        sequential_fixtures._bundle(0.95, "baseline", 1),
        sequential_fixtures._bundle(0.95, "candidate", 1),
        sequential_fixtures._policy(),
    )

    text = sequential_comparison_markdown(decided)
    assert "sequential regression check: PASS" in text
    assert "Latest metric bounds" in text

    waiting = sequential_comparison_markdown(undecided)
    assert "| n/a | n/a | CONTINUE |" in waiting
    assert "Latest metric bounds" not in waiting
