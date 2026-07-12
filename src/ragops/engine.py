from __future__ import annotations

from statistics import fmean

from ragops.evaluators import (
    citation_coverage,
    citation_precision,
    lexical_groundedness,
    redteam_findings,
)
from ragops.loader import ContractError
from ragops.models import (
    CaseResult,
    ComparisonReport,
    EvaluationReport,
    RecordedResponse,
    RegressionPolicy,
    Scenario,
)
from ragops.plugins import CaseEvaluator


def evaluate(
    scenario: Scenario,
    responses: tuple[RecordedResponse, ...],
    evaluators: tuple[CaseEvaluator, ...] = (),
) -> EvaluationReport:
    response_by_id = {response.case_id: response for response in responses}
    expected_ids = {case.id for case in scenario.cases}
    if set(response_by_id) != expected_ids:
        missing = sorted(expected_ids - set(response_by_id))
        unknown = sorted(set(response_by_id) - expected_ids)
        raise ContractError(f"Response coverage mismatch; missing={missing}, unknown={unknown}")

    result_items: list[CaseResult] = []
    for case in scenario.cases:
        response = response_by_id[case.id]
        custom_metrics: dict[str, float] = {}
        plugin_findings = []
        for evaluator in evaluators:
            plugin_result = evaluator.evaluate(case, response)
            for metric_name, value in plugin_result.metrics.items():
                key = f"{evaluator.name}.{metric_name}"
                if key in custom_metrics:
                    raise ValueError(f"Duplicate plugin metric: {key}")
                custom_metrics[key] = value
            plugin_findings.extend(plugin_result.findings)
        result_items.append(CaseResult(
            case_id=case.id,
            citation_coverage=citation_coverage(case, response),
            citation_precision=citation_precision(case, response),
            lexical_groundedness=lexical_groundedness(case, response),
            latency_ms=response.latency_ms,
            cost_usd=response.cost_usd,
            findings=redteam_findings(scenario.redteam, response) + tuple(plugin_findings),
            custom_metrics=custom_metrics,
        ))
    results = tuple(result_items)
    metrics = {
        "citation_coverage": fmean(result.citation_coverage for result in results),
        "citation_precision": fmean(result.citation_precision for result in results),
        "lexical_groundedness": fmean(result.lexical_groundedness for result in results),
        "avg_latency_ms": fmean(result.latency_ms for result in results),
        "avg_cost_usd": fmean(result.cost_usd for result in results),
        "critical_findings": float(
            sum(finding.severity == "critical" for result in results for finding in result.findings)
        ),
    }
    custom_metric_names = sorted({name for result in results for name in result.custom_metrics})
    for name in custom_metric_names:
        values = [result.custom_metrics[name] for result in results if name in result.custom_metrics]
        metrics[name] = fmean(values)
    thresholds = scenario.thresholds
    failed: list[str] = []
    if metrics["citation_coverage"] < thresholds.citation_coverage:
        failed.append("citation_coverage")
    if metrics["citation_precision"] < thresholds.citation_precision:
        failed.append("citation_precision")
    if metrics["lexical_groundedness"] < thresholds.lexical_groundedness:
        failed.append("lexical_groundedness")
    if metrics["avg_latency_ms"] > thresholds.max_latency_ms:
        failed.append("latency_budget")
    if metrics["avg_cost_usd"] > thresholds.max_cost_usd:
        failed.append("cost_budget")
    if metrics["critical_findings"] > 0:
        failed.append("critical_redteam_finding")

    return EvaluationReport(
        report_version="0.1",
        scenario_id=scenario.id,
        passed=not failed,
        metrics=metrics,
        failed_gates=tuple(failed),
        cases=results,
        metadata={"scenario_schema_version": scenario.schema_version},
    )


def compare(
    scenario: Scenario,
    baseline_responses: tuple[RecordedResponse, ...],
    candidate_responses: tuple[RecordedResponse, ...],
    policy: RegressionPolicy | None = None,
) -> ComparisonReport:
    """Compare a candidate build with a known baseline and apply regression gates."""
    policy = policy or RegressionPolicy()
    baseline = evaluate(scenario, baseline_responses)
    candidate = evaluate(scenario, candidate_responses)
    deltas = {
        "citation_coverage": candidate.metrics["citation_coverage"]
        - baseline.metrics["citation_coverage"],
        "citation_precision": candidate.metrics["citation_precision"]
        - baseline.metrics["citation_precision"],
        "lexical_groundedness": candidate.metrics["lexical_groundedness"]
        - baseline.metrics["lexical_groundedness"],
        "avg_latency_ms": candidate.metrics["avg_latency_ms"]
        - baseline.metrics["avg_latency_ms"],
        "avg_cost_usd": candidate.metrics["avg_cost_usd"]
        - baseline.metrics["avg_cost_usd"],
        "critical_findings": candidate.metrics["critical_findings"]
        - baseline.metrics["critical_findings"],
    }
    failed: list[str] = []
    if not candidate.passed:
        failed.append("candidate_release_gate")
    if deltas["citation_coverage"] < -policy.max_citation_coverage_drop:
        failed.append("citation_coverage_regression")
    if deltas["citation_precision"] < -policy.max_citation_precision_drop:
        failed.append("citation_precision_regression")
    if deltas["lexical_groundedness"] < -policy.max_groundedness_drop:
        failed.append("groundedness_regression")
    if deltas["avg_latency_ms"] > policy.max_latency_increase_ms:
        failed.append("latency_regression")
    if deltas["avg_cost_usd"] > policy.max_cost_increase_usd:
        failed.append("cost_regression")
    if deltas["critical_findings"] > 0:
        failed.append("new_critical_findings")

    return ComparisonReport(
        report_version="0.2",
        scenario_id=scenario.id,
        passed=not failed,
        baseline_passed=baseline.passed,
        candidate_passed=candidate.passed,
        deltas=deltas,
        failed_gates=tuple(failed),
        baseline=baseline,
        candidate=candidate,
    )
