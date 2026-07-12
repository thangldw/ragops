from __future__ import annotations

import argparse
import json
from pathlib import Path

from ragops.benchmarks import scenario_summary
from ragops.config import load_regression_policy
from ragops.engine import compare, evaluate
from ragops.loader import ContractError, load_responses, load_scenario
from ragops.plugins import (
    CaseEvaluator,
    CitationCorrectnessEvaluator,
    ClaimSupportEvaluator,
    RetrievalRecallEvaluator,
)
from ragops.reporters import comparison_html, comparison_markdown, evaluation_markdown
from ragops.store import ExperimentStore
from ragops.traces import load_trace_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ragops")
    commands = parser.add_subparsers(dest="command", required=True)
    evaluate_parser = commands.add_parser("evaluate", help="Evaluate recorded responses")
    evaluate_parser.add_argument("--scenario", required=True)
    evaluate_input = evaluate_parser.add_mutually_exclusive_group(required=True)
    evaluate_input.add_argument("--responses")
    evaluate_input.add_argument("--traces", help="Portable JSONL trace input")
    evaluate_parser.add_argument("--output")
    evaluate_parser.add_argument("--format", choices=("json", "markdown"), default="json")
    evaluate_parser.add_argument("--store")
    evaluate_parser.add_argument("--label", default="")
    evaluate_parser.add_argument(
        "--evaluator",
        action="append",
        choices=("retrieval_recall", "citation_correctness", "claim_support"),
        default=[],
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
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "inspect":
        try:
            summary = scenario_summary(load_scenario(args.scenario))
        except ContractError as exc:
            raise SystemExit(f"contract error: {exc}") from exc
        print(json.dumps(summary, ensure_ascii=False, indent=2))
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
            report = evaluate(
                scenario,
                load_trace_jsonl(args.traces) if args.traces else load_responses(args.responses),
                evaluators=_evaluators_from_names(args.evaluator),
            )
        else:
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


def _evaluators_from_names(names: list[str]) -> tuple[CaseEvaluator, ...]:
    factories = {
        "retrieval_recall": RetrievalRecallEvaluator,
        "citation_correctness": CitationCorrectnessEvaluator,
        "claim_support": ClaimSupportEvaluator,
    }
    return tuple(factories[name]() for name in names)


if __name__ == "__main__":
    raise SystemExit(main())
