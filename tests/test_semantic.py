import json
import sys
from pathlib import Path

import pytest

from ragops.loader import ContractError
from ragops.models import EvalCase, RecordedResponse
from ragops.semantic import CommandSemanticScorer, SemanticGroundingEvaluator


class FixedScorer:
    def __init__(self, value: float) -> None:
        self.value = value

    def score(self, evidence, claim) -> float:
        return self.value


def _run(evidence: str, answer: str):
    return EvalCase("c", "", (evidence,), ()), RecordedResponse("c", answer, (), 0, 0.0)


def test_semantic_score_supports_synonym_paraphrase() -> None:
    result = SemanticGroundingEvaluator(FixedScorer(0.9)).evaluate(
        *_run("Orders over 50 dollars ship free.", "Orders above 50 dollars qualify for free shipping.")
    )
    assert result.metrics["score"] == 1.0 and not result.findings


def test_guard_blocks_wrong_number_even_when_scorer_is_confident() -> None:
    evaluator = SemanticGroundingEvaluator(FixedScorer(0.99))
    result = evaluator.evaluate(*_run("Refunds last 30 days.", "Refunds last 60 days."))
    assert result.metrics["score"] == 0.0
    assert "contradict" in result.findings[0].message
    unguarded = SemanticGroundingEvaluator(FixedScorer(0.99), guard_with_strict=False)
    assert unguarded.evaluate(*_run("Refunds last 30 days.", "Refunds last 60 days.")).metrics["score"] == 1.0


def test_low_score_and_empty_answer() -> None:
    assert SemanticGroundingEvaluator(FixedScorer(0.1)).evaluate(*_run("A b.", "C d.")).metrics["score"] == 0.0
    assert SemanticGroundingEvaluator(FixedScorer(1.0)).evaluate(*_run("A b.", "")).metrics["score"] == 0.0
    with pytest.raises(ValueError):
        SemanticGroundingEvaluator(FixedScorer(1.0), threshold=2)


def _script(tmp_path: Path, body: str) -> tuple[str, ...]:
    path = tmp_path / "scorer.py"
    path.write_text(body, encoding="utf-8")
    return (sys.executable, str(path))


def test_command_scorer_round_trip_and_contract(tmp_path: Path) -> None:
    ok = _script(
        tmp_path,
        "import sys, json\nd = json.load(sys.stdin)\nprint(json.dumps({'score': 0.75 if d['claim'] else 0}))\n",
    )
    assert CommandSemanticScorer(ok).score(("e",), "claim") == 0.75

    for body in ("print('nope')", "print('{\"score\": 2}')", "import sys; sys.exit(3)", "print('{\"score\": true}')"):
        with pytest.raises(ContractError):
            CommandSemanticScorer(_script(tmp_path, body)).score(("e",), "claim")

    with pytest.raises(ValueError):
        CommandSemanticScorer(())
    with pytest.raises(ValueError):
        CommandSemanticScorer(ok, timeout_seconds=0)
    with pytest.raises(ContractError):
        CommandSemanticScorer(("definitely-not-a-real-binary-xyz",)).score(("e",), "c")


def test_cli_requires_semantic_command(tmp_path: Path) -> None:
    import subprocess

    base = [
        sys.executable, "-m", "ragops.cli", "evaluate", "--scenario",
        "scenarios/japanese_troubleshooting/scenario.json", "--responses",
        "scenarios/japanese_troubleshooting/sample_responses.json", "--evaluator", "semantic_grounding",
    ]
    missing = subprocess.run(base, capture_output=True, text=True)
    assert missing.returncode != 0 and "--semantic-command" in missing.stderr
    scorer = _script(tmp_path, "import json\nprint(json.dumps({'score': 1.0}))\n")
    done = subprocess.run([*base, "--semantic-command", " ".join(scorer)], capture_output=True, text=True)
    assert done.returncode in (0, 2), done.stderr
    assert "metrics" in json.loads(done.stdout) or "cases" in json.loads(done.stdout)
