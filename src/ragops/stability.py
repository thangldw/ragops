"""Stability gate: block when the same question gets noticeably different results across repeats.

A mean can stay flat while individual cases swing from good to bad between runs. This reads a replay
bundle (``ragops collect-runs``), measures per-case spread for each metric and can compare it with a
baseline bundle, so a candidate that became less repeatable is caught even if its average did not move.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from statistics import fmean, stdev
from typing import Any

from ragops.loader import ContractError
from ragops.models import ReplayBundle


@dataclass(frozen=True)
class MetricStability:
    metric: str
    cases_measured: int
    cases_with_single_run: int
    mean_stddev: float
    max_range: float
    unstable_cases: tuple[str, ...]
    unstable_fraction: float
    baseline_mean_stddev: float | None = None
    stddev_increase: float | None = None


@dataclass(frozen=True)
class StabilityReport:
    schema_version: str
    scenario_id: str
    decision: str
    max_range: float
    max_unstable_fraction: float
    max_stddev_increase: float | None
    metrics: tuple[MetricStability, ...]
    failed_gates: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return self.decision == "PASS"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _spread(bundle: ReplayBundle, metric: str) -> tuple[dict[str, float], dict[str, float], int]:
    """Per-case (stddev, range) for ``metric``, and how many cases had too few repeats to measure."""
    values: dict[str, list[float]] = {}
    for record in bundle.records:
        if metric in record.metrics:
            values.setdefault(record.case_id, []).append(record.metrics[metric])
    deviations: dict[str, float] = {}
    ranges: dict[str, float] = {}
    single = 0
    for case_id, observed in values.items():
        if len(observed) < 2:
            single += 1
            continue
        deviations[case_id] = stdev(observed)
        ranges[case_id] = max(observed) - min(observed)
    return deviations, ranges, single


def stability_report(
    bundle: ReplayBundle,
    *,
    metrics: tuple[str, ...] = (),
    max_range: float = 0.2,
    max_unstable_fraction: float = 0.1,
    baseline: ReplayBundle | None = None,
    max_stddev_increase: float | None = None,
) -> StabilityReport:
    for name, value in (("max_range", max_range), ("max_unstable_fraction", max_unstable_fraction)):
        if isinstance(value, bool) or not math.isfinite(value) or value < 0:
            raise ContractError(f"{name} must be a non-negative number")
    if max_unstable_fraction > 1:
        raise ContractError("max_unstable_fraction must be at most 1")
    if max_stddev_increase is not None and (not math.isfinite(max_stddev_increase) or max_stddev_increase < 0):
        raise ContractError("max_stddev_increase must be a non-negative number")
    if max_stddev_increase is not None and baseline is None:
        raise ContractError("max_stddev_increase needs a baseline bundle")
    if baseline is not None and baseline.scenario_id != bundle.scenario_id:
        raise ContractError("Baseline and candidate bundles are for different scenarios")
    names = metrics or tuple(sorted({name for record in bundle.records for name in record.metrics}))
    if not names:
        raise ContractError("The bundle has no metrics to measure")
    results: list[MetricStability] = []
    failed: list[str] = []
    for metric in names:
        deviations, ranges, single = _spread(bundle, metric)
        if not deviations:
            raise ContractError(
                f"Metric {metric!r} has no case with at least two repeats; collect more repeats"
            )
        unstable = tuple(sorted(case for case, spread in ranges.items() if spread > max_range))
        fraction = len(unstable) / len(deviations)
        mean_std = fmean(deviations.values())
        base_std = increase = None
        if baseline is not None:
            base_deviations, _, _ = _spread(baseline, metric)
            if not base_deviations:
                raise ContractError(f"Baseline has no case with at least two repeats for {metric!r}")
            base_std = fmean(base_deviations.values())
            increase = mean_std - base_std
        results.append(
            MetricStability(
                metric, len(deviations), single, mean_std, max(ranges.values()), unstable, fraction,
                base_std, increase,
            )
        )
        if fraction > max_unstable_fraction:
            failed.append(f"unstable_fraction:{metric}")
        if max_stddev_increase is not None and increase is not None and increase > max_stddev_increase:
            failed.append(f"stddev_increase:{metric}")
    return StabilityReport(
        "1.0", bundle.scenario_id, "PASS" if not failed else "BLOCK", max_range,
        max_unstable_fraction, max_stddev_increase, tuple(results), tuple(failed),
    )


def stability_markdown(report: StabilityReport) -> str:
    lines = [
        f"## RAGOps stability gate: {report.decision}",
        "",
        f"Scenario: `{report.scenario_id}`. A case is unstable when a metric varies by more than "
        f"{report.max_range:g} between repeats; at most {report.max_unstable_fraction:.0%} of cases may be unstable.",
        "",
        "| Metric | Cases | Mean stddev | Largest range | Unstable | Result |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in report.metrics:
        bad = (
            f"unstable_fraction:{item.metric}" in report.failed_gates
            or f"stddev_increase:{item.metric}" in report.failed_gates
        )
        lines.append(
            f"| `{item.metric}` | {item.cases_measured} | {item.mean_stddev:.4g} | {item.max_range:.4g} | "
            f"{len(item.unstable_cases)} ({item.unstable_fraction:.0%}) | {'BLOCK' if bad else 'PASS'} |"
        )
    for item in report.metrics:
        if item.stddev_increase is not None:
            lines.append(
                f"- `{item.metric}`: mean stddev {item.baseline_mean_stddev:.4g} -> {item.mean_stddev:.4g} "
                f"({item.stddev_increase:+.4g})"
            )
        if item.unstable_cases:
            shown = ", ".join(f"`{case}`" for case in item.unstable_cases[:10])
            more = len(item.unstable_cases) - 10
            lines.append(f"- `{item.metric}` unstable cases: {shown}" + (f" (+{more} more)" if more > 0 else ""))
        if item.cases_with_single_run:
            lines.append(f"- `{item.metric}`: {item.cases_with_single_run} case(s) skipped, only one repeat")
    return "\n".join(lines) + "\n"
