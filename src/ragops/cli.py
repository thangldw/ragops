from __future__ import annotations

import argparse
import json
from pathlib import Path

from ragops.config import load_regression_policy
from ragops.engine import compare, evaluate
from ragops.loader import ContractError, load_responses, load_scenario
from ragops.reporters import comparison_html, comparison_markdown, evaluation_markdown
from ragops.store import ExperimentStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ragops")
    commands = parser.add_subparsers(dest="command", required=True)
    evaluate_parser = commands.add_parser("evaluate", help="Evaluate recorded responses")
    evaluate_parser.add_argument("--scenario", required=True)
    evaluate_parser.add_argument("--responses", required=True)
    evaluate_parser.add_argument("--output")
    evaluate_parser.add_argument("--format", choices=("json", "markdown"), default="json")
    evaluate_parser.add_argument("--store")
    evaluate_parser.add_argument("--label", default="")
    compare_parser = commands.add_parser("compare", help="Compare candidate responses to baseline")
    compare_parser.add_argument("--scenario", required=True)
    compare_parser.add_argument("--baseline", required=True)
    compare_parser.add_argument("--candidate", required=True)
    compare_parser.add_argument("--output")
    compare_parser.add_argument("--format", choices=("json", "markdown", "html"), default="markdown")
    compare_parser.add_argument("--store")
    compare_parser.add_argument("--label", default="")
    compare_parser.add_argument("--policy", help="TOML regression policy")
    history_parser = commands.add_parser("history", help="List saved experiment runs")
    history_parser.add_argument("--store", required=True)
    history_parser.add_argument("--limit", type=int, default=20)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "history":
        runs = ExperimentStore(args.store).list_runs(limit=args.limit)
        print(json.dumps(runs, ensure_ascii=False, indent=2))
        return 0
    try:
        scenario = load_scenario(args.scenario)
        if args.command == "evaluate":
            report = evaluate(scenario, load_responses(args.responses))
        else:
            report = compare(
                scenario,
                load_responses(args.baseline),
                load_responses(args.candidate),
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


if __name__ == "__main__":
    raise SystemExit(main())
