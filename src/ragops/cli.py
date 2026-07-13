from __future__ import annotations

import argparse
import json
from pathlib import Path

from ragops.adapters.external_metrics import (
    load_external_metric_evaluator,
    validate_external_metric_pair,
)
from ragops.benchmarks import scenario_summary
from ragops.config import load_evaluation_policy, load_regression_policy
from ragops.control_plane import ControlPlane
from ragops.demo import DEFAULT_DEMO_SCENARIO, DEMO_BUNDLES, write_demo
from ragops.engine import compare, evaluate
from ragops.loader import ContractError, load_responses, load_scenario
from ragops.plugins import (
    AnswerLengthBudgetEvaluator,
    CaseEvaluator,
    CitationCorrectnessEvaluator,
    ClaimSupportEvaluator,
    RetrievalRecallEvaluator,
)
from ragops.pilot import (
    PilotContractError,
    load_pilot_economics,
    load_pilot_manifest,
    load_pilot_observations,
    pilot_markdown,
    summarize_pilot,
)
from ragops.reporters import comparison_html, comparison_markdown, evaluation_markdown
from ragops.store import ExperimentStore
from ragops.traces import load_trace_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ragops")
    commands = parser.add_subparsers(dest="command", required=True)
    demo_parser = commands.add_parser("demo", help="Generate a credential-free release-gate demo")
    demo_parser.add_argument("--output", default="ragops-demo")
    demo_parser.add_argument(
        "--scenario",
        choices=tuple(sorted(DEMO_BUNDLES)),
        default=DEFAULT_DEMO_SCENARIO,
        help="Credential-free workflow scenario to generate",
    )
    demo_parser.add_argument(
        "--force",
        action="store_true",
        help="Replace regular demo files in an existing non-symlink directory",
    )
    evaluate_parser = commands.add_parser("evaluate", help="Evaluate recorded responses")
    evaluate_parser.add_argument("--scenario", required=True)
    evaluate_input = evaluate_parser.add_mutually_exclusive_group(required=True)
    evaluate_input.add_argument("--responses")
    evaluate_input.add_argument("--traces", help="Portable JSONL trace input")
    evaluate_parser.add_argument("--output")
    evaluate_parser.add_argument("--format", choices=("json", "markdown"), default="json")
    evaluate_parser.add_argument("--store")
    evaluate_parser.add_argument("--label", default="")
    evaluate_parser.add_argument("--evaluation-policy", help="TOML evaluator gate policy")
    evaluate_parser.add_argument(
        "--external-metrics",
        help="Portable per-case metric envelope from Ragas, DeepEval, Langfuse, or custom",
    )
    evaluate_parser.add_argument(
        "--evaluator",
        action="append",
        choices=(
            "retrieval_recall",
            "citation_correctness",
            "claim_support",
            "answer_length_budget",
        ),
        default=[],
    )
    evaluate_parser.add_argument(
        "--answer-length-limit",
        type=int,
        default=500,
        help="Unicode code-point limit for answer_length_budget (default: 500)",
    )
    compare_parser = commands.add_parser("compare", help="Compare candidate responses to baseline")
    compare_parser.add_argument("--scenario", required=True)
    baseline_input = compare_parser.add_mutually_exclusive_group(required=True)
    baseline_input.add_argument("--baseline")
    baseline_input.add_argument("--baseline-traces")
    candidate_input = compare_parser.add_mutually_exclusive_group(required=True)
    candidate_input.add_argument("--candidate")
    candidate_input.add_argument("--candidate-traces")
    compare_parser.add_argument("--output")
    compare_parser.add_argument("--format", choices=("json", "markdown", "html"), default="markdown")
    compare_parser.add_argument("--store")
    compare_parser.add_argument("--label", default="")
    compare_parser.add_argument("--policy", help="TOML regression policy")
    compare_parser.add_argument("--evaluation-policy", help="TOML evaluator gate policy")
    compare_parser.add_argument(
        "--baseline-external-metrics",
        help="Portable baseline per-case external metric envelope",
    )
    compare_parser.add_argument(
        "--candidate-external-metrics",
        help="Portable candidate per-case external metric envelope",
    )
    compare_parser.add_argument(
        "--evaluator",
        action="append",
        choices=(
            "retrieval_recall",
            "citation_correctness",
            "claim_support",
            "answer_length_budget",
        ),
        default=[],
    )
    compare_parser.add_argument(
        "--answer-length-limit",
        type=int,
        default=500,
        help="Unicode code-point limit for answer_length_budget (default: 500)",
    )
    history_parser = commands.add_parser("history", help="List saved experiment runs")
    history_parser.add_argument("--store", required=True)
    history_parser.add_argument("--limit", type=int, default=20)
    review_parser = commands.add_parser("review", help="Review a saved experiment run")
    review_parser.add_argument("--store", required=True)
    review_parser.add_argument("--run-id", required=True)
    review_parser.add_argument(
        "--status", required=True, choices=("accepted", "rejected", "needs_changes")
    )
    review_parser.add_argument("--reviewer", required=True)
    review_parser.add_argument("--note", default="")
    trend_parser = commands.add_parser("trend", help="Read a saved metric trend")
    trend_parser.add_argument("--store", required=True)
    trend_parser.add_argument("--scenario-id", required=True)
    trend_parser.add_argument("--metric", required=True)
    trend_parser.add_argument("--limit", type=int, default=50)
    inspect_parser = commands.add_parser("inspect", help="Inspect scenario benchmark coverage")
    inspect_parser.add_argument("--scenario", required=True)
    workspace_create = commands.add_parser("workspace-create", help="Create an alpha workspace")
    workspace_create.add_argument("--root", required=True)
    workspace_create.add_argument("--workspace-id", required=True)
    workspace_create.add_argument("--name", required=True)
    workspace_rotate = commands.add_parser("workspace-rotate-key", help="Rotate a workspace key")
    workspace_rotate.add_argument("--root", required=True)
    workspace_rotate.add_argument("--workspace-id", required=True)
    workspace_rotate.add_argument("--current-key", required=True)
    workspace_audit = commands.add_parser("workspace-audit", help="Read workspace audit events")
    workspace_audit.add_argument("--root", required=True)
    workspace_audit.add_argument("--workspace-id", required=True)
    workspace_audit.add_argument("--limit", type=int, default=100)
    pilot_parser = commands.add_parser(
        "pilot-report", help="Summarize design-partner adoption and ROI evidence"
    )
    pilot_parser.add_argument("--manifest", required=True)
    pilot_parser.add_argument("--observations", required=True)
    pilot_parser.add_argument("--economics")
    pilot_parser.add_argument("--output")
    pilot_parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "demo":
        try:
            summary = write_demo(args.output, force=args.force, scenario_id=args.scenario)
        except (OSError, ValueError) as exc:
            raise SystemExit(f"demo output error: {exc}") from exc
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    if args.command == "inspect":
        try:
            summary = scenario_summary(load_scenario(args.scenario))
        except ContractError as exc:
            raise SystemExit(f"contract error: {exc}") from exc
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    if args.command == "workspace-create":
        try:
            key = ControlPlane(args.root).create_workspace(args.workspace_id, args.name)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps({"workspace_id": args.workspace_id, "api_key": key}))
        return 0
    if args.command == "workspace-rotate-key":
        try:
            key = ControlPlane(args.root).rotate_key(args.workspace_id, args.current_key)
        except (PermissionError, ValueError) as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps({"workspace_id": args.workspace_id, "api_key": key}))
        return 0
    if args.command == "workspace-audit":
        events = ControlPlane(args.root).audit_events(args.workspace_id, limit=args.limit)
        print(json.dumps(events, ensure_ascii=False, indent=2))
        return 0
    if args.command == "pilot-report":
        try:
            report = summarize_pilot(
                load_pilot_manifest(args.manifest),
                load_pilot_observations(args.observations),
                load_pilot_economics(args.economics) if args.economics else None,
            )
        except PilotContractError as exc:
            raise SystemExit(f"pilot contract error: {exc}") from exc
        rendered = (
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
            if args.format == "json"
            else pilot_markdown(report)
        )
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered.rstrip() + "\n", encoding="utf-8")
        else:
            print(rendered.rstrip())
        return 0
    if args.command == "history":
        runs = ExperimentStore(args.store).list_runs(limit=args.limit)
        print(json.dumps(runs, ensure_ascii=False, indent=2))
        return 0
    if args.command == "review":
        try:
            ExperimentStore(args.store).review(
                args.run_id,
                status=args.status,
                reviewer=args.reviewer,
                note=args.note,
            )
        except (KeyError, ValueError) as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps({"run_id": args.run_id, "review_status": args.status}))
        return 0
    if args.command == "trend":
        points = ExperimentStore(args.store).metric_trend(
            args.scenario_id,
            args.metric,
            limit=args.limit,
        )
        print(json.dumps(points, ensure_ascii=False, indent=2))
        return 0
    try:
        scenario = load_scenario(args.scenario)
        if args.command == "evaluate":
            evaluators = _evaluators_from_names(
                args.evaluator,
                answer_length_limit=args.answer_length_limit,
            )
            if args.external_metrics:
                evaluators += (load_external_metric_evaluator(args.external_metrics, scenario),)
            report = evaluate(
                scenario,
                load_trace_jsonl(args.traces) if args.traces else load_responses(args.responses),
                evaluators=evaluators,
                policy=(
                    load_evaluation_policy(args.evaluation_policy)
                    if args.evaluation_policy
                    else None
                ),
            )
        else:
            if bool(args.baseline_external_metrics) != bool(args.candidate_external_metrics):
                raise ContractError(
                    "Compare needs both --baseline-external-metrics and "
                    "--candidate-external-metrics"
                )
            evaluators = _evaluators_from_names(
                args.evaluator,
                answer_length_limit=args.answer_length_limit,
            )
            if args.baseline_external_metrics:
                baseline_external = load_external_metric_evaluator(
                    args.baseline_external_metrics, scenario
                )
                candidate_external = load_external_metric_evaluator(
                    args.candidate_external_metrics, scenario
                )
                validate_external_metric_pair(baseline_external, candidate_external)
            report = compare(
                scenario,
                (
                    load_trace_jsonl(args.baseline_traces)
                    if args.baseline_traces
                    else load_responses(args.baseline)
                ),
                (
                    load_trace_jsonl(args.candidate_traces)
                    if args.candidate_traces
                    else load_responses(args.candidate)
                ),
                policy=load_regression_policy(args.policy) if args.policy else None,
                evaluators=evaluators,
                baseline_evaluators=(
                    evaluators + (baseline_external,)
                    if args.baseline_external_metrics
                    else None
                ),
                candidate_evaluators=(
                    evaluators + (candidate_external,)
                    if args.candidate_external_metrics
                    else None
                ),
                evaluation_policy=(
                    load_evaluation_policy(args.evaluation_policy)
                    if args.evaluation_policy
                    else None
                ),
            )
    except (ContractError, ValueError) as exc:
        raise SystemExit(f"contract error: {exc}") from exc
    if args.format == "json":
        rendered = json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
    elif args.command == "evaluate":
        rendered = evaluation_markdown(report)
    elif args.format == "html":
        rendered = comparison_html(report)
    else:
        rendered = comparison_markdown(report)
    if args.store:
        ExperimentStore(args.store).save(report, label=args.label)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered.rstrip() + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0 if report.passed else 2


def _evaluators_from_names(
    names: list[str],
    *,
    answer_length_limit: int = 500,
) -> tuple[CaseEvaluator, ...]:
    factories = {
        "retrieval_recall": RetrievalRecallEvaluator,
        "citation_correctness": CitationCorrectnessEvaluator,
        "claim_support": ClaimSupportEvaluator,
        "answer_length_budget": lambda: AnswerLengthBudgetEvaluator(
            max_characters=answer_length_limit
        ),
    }
    return tuple(factories[name]() for name in names)


if __name__ == "__main__":
    raise SystemExit(main())
