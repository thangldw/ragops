"""Pluggable semantic grounding. The core stays offline: scoring is delegated to a
user-supplied command or Python callable, and its scores are plain metrics."""

from __future__ import annotations

import json
import math
import subprocess
from typing import Protocol

from ragops.evaluators import claim_conflict, split_sentences
from ragops.loader import ContractError
from ragops.models import EvalCase, Finding, RecordedResponse
from ragops.plugins import PluginResult

MAX_OUTPUT_BYTES = 10_000


class SemanticScorer(Protocol):
    def score(self, evidence: tuple[str, ...], claim: str) -> float:
        """Return how well ``evidence`` supports ``claim``, from 0.0 to 1.0."""


class CommandSemanticScorer:
    """Run an explicit command (no shell) per claim.

    stdin:  {"evidence": [str, ...], "claim": str}
    stdout: {"score": float between 0 and 1}
    """

    def __init__(self, command: tuple[str, ...], *, timeout_seconds: float = 60.0) -> None:
        if not command or any(not isinstance(part, str) or not part for part in command):
            raise ValueError("Semantic scorer command must contain non-empty arguments")
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("Semantic scorer timeout must be finite and positive")
        self.command = command
        self.timeout_seconds = timeout_seconds

    def score(self, evidence: tuple[str, ...], claim: str) -> float:
        payload = json.dumps({"evidence": list(evidence), "claim": claim}, ensure_ascii=False)
        try:
            completed = subprocess.run(
                self.command,
                input=payload.encode("utf-8"),
                capture_output=True,
                check=False,
                timeout=self.timeout_seconds,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ContractError(f"Semantic scorer failed: {exc}") from exc
        if completed.returncode != 0:
            error = completed.stderr[:2000].decode("utf-8", errors="replace").strip()
            raise ContractError(f"Semantic scorer exited {completed.returncode}: {error}")
        if len(completed.stdout) > MAX_OUTPUT_BYTES:
            raise ContractError("Semantic scorer output is too large")
        try:
            data = json.loads(completed.stdout.decode("utf-8"))
            value = data["score"]
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
            raise ContractError('Semantic scorer must print {"score": number}') from exc
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise ContractError("Semantic scorer score must be a number")
        if not math.isfinite(value) or not 0 <= value <= 1:
            raise ContractError("Semantic scorer score must be between 0 and 1")
        return float(value)


class SemanticGroundingEvaluator:
    """Claim-level grounding using an external semantic scorer.

    With ``guard_with_strict`` (default) a claim is never supported if it states a
    number/identifier absent from the evidence or flips its polarity, because
    semantic scorers commonly miss those errors.
    """

    name = "semantic_grounding"

    def __init__(
        self, scorer: SemanticScorer, *, threshold: float = 0.5, guard_with_strict: bool = True
    ) -> None:
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")
        self.scorer = scorer
        self.threshold = threshold
        self.guard_with_strict = guard_with_strict

    def evaluate(self, case: EvalCase, response: RecordedResponse) -> PluginResult:
        claims = split_sentences(response.answer)
        if not claims:
            return PluginResult(
                metrics={"score": 0.0, "min_claim_score": 0.0, "unsupported_claims": 1.0}
            )
        sentences = split_sentences(" ".join(case.evidence))
        scores, supported, conflicts = [], 0, 0
        for claim in claims:
            value = self.scorer.score(case.evidence, claim)
            scores.append(value)
            conflict = self.guard_with_strict and claim_conflict(claim, sentences)
            conflicts += bool(conflict)
            supported += value >= self.threshold and not conflict
        unsupported = len(claims) - supported
        findings: tuple[Finding, ...] = ()
        if unsupported:
            findings = (
                Finding(
                    rule="unsupported_claim",
                    severity="high",
                    message=(
                        f"{unsupported} of {len(claims)} claim(s) lack semantic support"
                        + (f" ({conflicts} contradict numbers or polarity)" if conflicts else "")
                    ),
                ),
            )
        return PluginResult(
            metrics={
                "score": supported / len(claims),
                "min_claim_score": min(scores),
                "unsupported_claims": float(unsupported),
            },
            findings=findings,
        )
