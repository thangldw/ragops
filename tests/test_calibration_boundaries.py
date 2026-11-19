"""Boundary and exact-value tests found by mutation testing (mutmut) on calibration."""

import pytest

from ragops.calibration import (
    CalibrationPolicy,
    CalibrationRecord,
    HumanLabel,
    calibrate_evaluator,
    suggest_threshold,
)


def _policy(**overrides: float) -> CalibrationPolicy:
    values = {
        "threshold": 0.5,
        "minimum_coverage": 0.0,
        "minimum_accuracy": 0.0,
        "maximum_mae": 1.0,
        "maximum_false_pass_rate": 1.0,
        "minimum_agreement": 0.0,
    }
    values.update(overrides)
    return CalibrationPolicy(**values)


def _rec(case_id: str, score: float, *labels: int) -> CalibrationRecord:
    return CalibrationRecord(case_id, score, tuple(HumanLabel(f"r{i}", label) for i, label in enumerate(labels)))


def test_scores_and_mean_labels_equal_to_the_threshold_count_as_pass() -> None:
    report = calibrate_evaluator("e", (_rec("a", 0.5, 1, 0), _rec("b", 0.4, 0, 0)), _policy())

    assert report.accuracy == 1.0
    assert report.false_pass_rate == 0.0 and report.false_block_rate == 0.0


def test_report_fields_and_empty_label_defaults() -> None:
    report = calibrate_evaluator("groundedness", (_rec("a", 0.9),), _policy())

    assert report.schema_version == "1.0" and report.evaluator == "groundedness"
    assert (report.case_count, report.labeled_case_count, report.reviewer_pair_count) == (1, 0, 0)
    assert (report.coverage, report.accuracy, report.mae) == (0.0, 0.0, 1.0)
    assert (report.false_pass_rate, report.false_block_rate) == (0.0, 0.0)
    assert report.reviewer_agreement is None and report.suggested_threshold is None
    assert report.to_dict()["schema_version"] == "1.0"


def test_each_failed_gate_is_named_exactly() -> None:
    records = (_rec("a", 0.9, 0), _rec("b", 0.1, 1), _rec("c", 0.5))
    report = calibrate_evaluator(
        "e",
        records,
        _policy(minimum_coverage=1.0, minimum_accuracy=0.5, maximum_mae=0.1, maximum_false_pass_rate=0.0),
    )

    assert report.failed_gates == ("coverage", "accuracy", "mae", "false_pass_rate")
    assert report.decision == "BLOCK"
    assert report.false_pass_rate == 0.5 and report.false_block_rate == 0.5


def test_agreement_gates_and_their_boundaries() -> None:
    one_reviewer = (_rec("a", 0.9, 1), _rec("b", 0.1, 0))
    assert calibrate_evaluator("e", one_reviewer, _policy(minimum_agreement=0.0)).failed_gates == ()
    assert calibrate_evaluator("e", one_reviewer, _policy(minimum_agreement=0.5)).failed_gates == (
        "reviewer_agreement_insufficient",
    )
    pair = (_rec("a", 0.9, 1, 1), _rec("b", 0.1, 0, 0))
    assert calibrate_evaluator("e", pair, _policy(minimum_agreement=1.0)).failed_gates == ()
    disagree = (_rec("a", 0.9, 1, 0), _rec("b", 0.1, 0, 1))
    report = calibrate_evaluator("e", disagree, _policy(minimum_agreement=0.0))
    assert report.reviewer_agreement == pytest.approx(-1.0)
    assert calibrate_evaluator("e", disagree, _policy(minimum_agreement=0.5)).failed_gates == ("reviewer_agreement",)


def test_reviewer_agreement_is_cohens_kappa_and_skips_thin_overlap() -> None:
    records = (
        CalibrationRecord("a", 0.5, (HumanLabel("x", 1), HumanLabel("y", 1))),
        CalibrationRecord("b", 0.5, (HumanLabel("x", 1), HumanLabel("y", 1))),
        CalibrationRecord("c", 0.5, (HumanLabel("x", 1), HumanLabel("y", 0))),
        CalibrationRecord("d", 0.5, (HumanLabel("x", 0), HumanLabel("y", 0))),
        CalibrationRecord("e", 0.5, (HumanLabel("z", 1),)),
    )
    report = calibrate_evaluator("e", records, _policy())

    # x/y: observed 3/4, yes rates 3/4 and 2/4 -> expected 0.5 -> kappa 0.5; z overlaps nobody.
    assert report.reviewer_agreement == pytest.approx(0.5)
    assert report.reviewer_pair_count == 1


def test_two_shared_cases_are_enough_and_one_is_not() -> None:
    two = (_rec("a", 0.5, 1, 1), _rec("b", 0.5, 0, 0))
    one = (_rec("a", 0.5, 1, 1), _rec("b", 0.5, 0))
    assert calibrate_evaluator("e", two, _policy()).reviewer_pair_count == 1
    assert calibrate_evaluator("e", one, _policy()).reviewer_pair_count == 0


def test_a_thin_pair_does_not_stop_later_pairs() -> None:
    records = (
        CalibrationRecord("a", 0.5, (HumanLabel("a1", 1), HumanLabel("b1", 1), HumanLabel("c1", 1))),
        CalibrationRecord("b", 0.5, (HumanLabel("b1", 0), HumanLabel("c1", 0))),
    )
    # a1 overlaps the others on one case only (skipped); b1 and c1 share two and agree fully.
    report = calibrate_evaluator("e", records, _policy())
    assert report.reviewer_pair_count == 1 and report.reviewer_agreement == 1.0


def test_threshold_suggestion_exact_values() -> None:
    records = (_rec("a", 0.2, 0), _rec("b", 0.6, 1))
    s = suggest_threshold(records, _policy(threshold=0.4))
    assert s is not None
    assert (s.threshold, s.accuracy, s.false_pass_rate, s.false_block_rate) == (0.4, 1.0, 0.0, 0.0)


def test_threshold_suggestion_can_block_everything() -> None:
    s = suggest_threshold((_rec("a", 0.9, 0), _rec("b", 0.8, 0)), _policy(maximum_false_pass_rate=0.0))
    assert s is not None and s.threshold == 0.91 and s.accuracy == 1.0 and s.meets_false_pass_limit


def test_threshold_suggestion_reports_false_blocks() -> None:
    records = (_rec("a", 0.9, 0), _rec("b", 0.9, 1), _rec("c", 0.3, 1))
    s = suggest_threshold(records, _policy(maximum_false_pass_rate=0.0))
    assert s is not None and s.meets_false_pass_limit
    assert s.threshold == 0.91
    assert s.false_pass_rate == 0.0
    assert s.false_block_rate == pytest.approx(2 / 3)
    assert s.accuracy == pytest.approx(1 / 3)


def test_threshold_suggestion_when_the_limit_cannot_be_met_prefers_fewest_false_passes() -> None:
    records = (_rec("a", 1.0, 0), _rec("b", 1.0, 1), _rec("c", 0.5, 0))
    s = suggest_threshold(records, _policy(threshold=0.9, maximum_false_pass_rate=0.0))
    assert s is not None and not s.meets_false_pass_limit
    assert s.false_pass_rate == pytest.approx(1 / 3)
    assert s.accuracy == pytest.approx(2 / 3)
    assert s.threshold == 1.0  # tie with 0.75; closer to the current threshold 0.9


def test_threshold_suggestion_prefers_the_threshold_closest_to_the_current_one() -> None:
    records = (_rec("a", 0.2, 0), _rec("b", 0.8, 1))
    near_low = suggest_threshold(records, _policy(threshold=0.3))
    near_high = suggest_threshold(records, _policy(threshold=0.8))
    assert near_low is not None and near_low.threshold == 0.5
    assert near_high is not None and near_high.threshold == 0.8


def test_threshold_suggestion_prefers_accuracy_among_thresholds_within_the_limit() -> None:
    records = (_rec("a", 0.9, 0), _rec("b", 0.9, 1), _rec("c", 0.3, 1), _rec("d", 0.1, 0))
    s = suggest_threshold(records, _policy(maximum_false_pass_rate=0.5))
    assert s is not None and s.meets_false_pass_limit
    assert s.threshold == 0.3 and s.accuracy == 0.75 and s.false_pass_rate == 0.25
