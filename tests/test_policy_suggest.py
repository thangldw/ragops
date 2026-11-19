from datetime import UTC, datetime
from pathlib import Path

import pytest

from ragops.cli import main
from ragops.engine import evaluate
from ragops.loader import ContractError, load_responses, load_scenario
from ragops.policy_suggest import suggest_release_policy
from ragops.policy_v2 import apply_release_policy, load_release_policy_v2

SCENARIO = Path("scenarios/japanese_troubleshooting")


def _load():
    scenario = load_scenario(SCENARIO / "scenario.json")
    return scenario, evaluate(scenario, load_responses(SCENARIO / "sample_responses.json"))


def test_suggested_policy_loads_and_the_baseline_passes_its_own_policy(tmp_path):
    scenario, baseline = _load()
    path = tmp_path / "policy.toml"
    path.write_text(suggest_release_policy(scenario, baseline, min_cases=1), encoding="utf-8")

    policy = load_release_policy_v2(path)
    assert {item.selector.name for item in policy.slices} >= {"category_direct_procedure"}
    assert all(item.selector.name != "language_ja" for item in policy.slices)  # covers every case
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    assert apply_release_policy(policy, baseline, baseline, scenario, now=now).decision == "PASS"


def test_suggested_policy_blocks_a_regressed_candidate(tmp_path):
    scenario, baseline = _load()
    path = tmp_path / "policy.toml"
    path.write_text(suggest_release_policy(scenario, baseline, min_cases=1), encoding="utf-8")
    regressed = evaluate(scenario, load_responses(SCENARIO / "regressed_responses.json"))
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    decision = apply_release_policy(load_release_policy_v2(path), baseline, regressed, scenario, now=now)

    assert decision.decision == "BLOCK"


def test_small_slices_are_skipped_and_arguments_are_validated():
    scenario, baseline = _load()
    assert "[[slices]]" not in suggest_release_policy(scenario, baseline, min_cases=len(scenario.cases) + 1)
    with pytest.raises(ContractError):
        suggest_release_policy(scenario, baseline, margin=2.0)
    with pytest.raises(ContractError):
        suggest_release_policy(scenario, baseline, min_cases=0)


def test_policy_suggest_cli_writes_a_policy(tmp_path, monkeypatch):
    out = tmp_path / "nested" / "policy.toml"
    monkeypatch.setattr(
        "sys.argv",
        ["ragops", "policy-suggest", "--scenario", str(SCENARIO / "scenario.json"),
         "--baseline", str(SCENARIO / "sample_responses.json"), "--min-cases", "1", "--output", str(out)],
    )
    assert main() == 0
    assert load_release_policy_v2(out).metrics
