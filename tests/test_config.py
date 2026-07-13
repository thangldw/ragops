import pytest

from ragops.config import load_evaluation_policy, load_regression_policy


def test_loads_regression_policy() -> None:
    policy = load_regression_policy("ragops.toml")

    assert policy.max_groundedness_drop == 0.05
    assert policy.max_citation_precision_drop == 0.0
    assert policy.max_latency_increase_ms == 250.0


def test_rejects_invalid_policy(tmp_path) -> None:
    path = tmp_path / "bad.toml"
    path.write_text("not toml", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid regression policy"):
        load_regression_policy(path)


def test_loads_evaluation_metric_and_finding_gates(tmp_path) -> None:
    path = tmp_path / "evaluation.toml"
    path.write_text(
        '[metrics.claim_support]\nminimum = 0.9\n\n'
        '[metrics."answer_length_budget.character_count"]\nmaximum = 500\n\n'
        '[findings]\nfail_on_severity = "high"\n',
        encoding="utf-8",
    )

    policy = load_evaluation_policy(path)

    assert policy.metric_gates["claim_support"].minimum == 0.9
    assert policy.metric_gates["answer_length_budget.character_count"].maximum == 500
    assert policy.fail_on_severity == "high"


@pytest.mark.parametrize(
    "content, message",
    [
        ('[metrics.claim_support]\nminimum = 0.9\nmaximum = 1.0\n', "exactly one"),
        ('[metrics.claim_support]\nminimum = nan\n', "finite"),
        ('[findings]\nfail_on_severity = "urgent"\n', "low, medium, high, or critical"),
    ],
)
def test_rejects_invalid_evaluation_policy(tmp_path, content: str, message: str) -> None:
    path = tmp_path / "evaluation.toml"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_evaluation_policy(path)
