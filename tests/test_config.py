import pytest

from ragops.config import load_regression_policy


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
