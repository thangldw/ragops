from __future__ import annotations

import math
import tomllib
from pathlib import Path

from ragops.models import EvaluationPolicy, MetricGate, RegressionPolicy


def load_regression_policy(path: str | Path) -> RegressionPolicy:
    try:
        data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
        policy = RegressionPolicy(**data["regression"])
        for name, value in (
            ("max_citation_coverage_drop", policy.max_citation_coverage_drop),
            ("max_citation_precision_drop", policy.max_citation_precision_drop),
            ("max_groundedness_drop", policy.max_groundedness_drop),
            ("max_latency_increase_ms", policy.max_latency_increase_ms),
            ("max_cost_increase_usd", policy.max_cost_increase_usd),
        ):
            if _finite_number(value, f"regression.{name}") < 0:
                raise ValueError(f"regression.{name} must be non-negative")
        return policy
    except (OSError, tomllib.TOMLDecodeError, KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Invalid regression policy {path}: {exc}") from exc


def load_evaluation_policy(path: str | Path) -> EvaluationPolicy:
    try:
        data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
        raw_metrics = data.get("metrics", {})
        if not isinstance(raw_metrics, dict):
            raise TypeError("metrics must be a table")
        metric_gates: dict[str, MetricGate] = {}
        for name, raw_gate in raw_metrics.items():
            if not isinstance(name, str) or not name:
                raise ValueError("metric names must be non-empty strings")
            if not isinstance(raw_gate, dict):
                raise TypeError(f"metric gate {name!r} must be a table")
            unknown = set(raw_gate) - {"minimum", "maximum"}
            if unknown:
                raise ValueError(f"metric gate {name!r} has unknown fields: {sorted(unknown)}")
            if ("minimum" in raw_gate) == ("maximum" in raw_gate):
                raise ValueError(
                    f"metric gate {name!r} must define exactly one of minimum or maximum"
                )
            minimum = _finite_number(raw_gate["minimum"], f"metrics.{name}.minimum") if "minimum" in raw_gate else None
            maximum = _finite_number(raw_gate["maximum"], f"metrics.{name}.maximum") if "maximum" in raw_gate else None
            metric_gates[name] = MetricGate(minimum=minimum, maximum=maximum)
        raw_findings = data.get("findings", {})
        if not isinstance(raw_findings, dict):
            raise TypeError("findings must be a table")
        unknown_findings = set(raw_findings) - {"fail_on_severity"}
        if unknown_findings:
            raise ValueError(f"findings has unknown fields: {sorted(unknown_findings)}")
        severity = raw_findings.get("fail_on_severity", "critical")
        if severity not in {"low", "medium", "high", "critical"}:
            raise ValueError("findings.fail_on_severity must be low, medium, high, or critical")
        return EvaluationPolicy(metric_gates=metric_gates, fail_on_severity=severity)
    except (OSError, tomllib.TOMLDecodeError, TypeError, ValueError) as exc:
        raise ValueError(f"Invalid evaluation policy {path}: {exc}") from exc


def _finite_number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result
