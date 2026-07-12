from __future__ import annotations

import argparse
import json
from pathlib import Path

from ragops.traces import write_trace_jsonl

from .agent import TroubleshootingAgent, result_as_dict


def main() -> int:
    parser = argparse.ArgumentParser(prog="jp-troubleshooting-agent")
    parser.add_argument("question", nargs="?")
    parser.add_argument("--role", default="engineer")
    parser.add_argument("--suite", help="JSON list containing case_id, question, and role")
    parser.add_argument("--output", help="Trace JSONL output for --suite")
    parser.add_argument("--retriever", choices=("graph", "lexical"), default="graph")
    args = parser.parse_args()
    agent = TroubleshootingAgent(graph_enabled=args.retriever == "graph")
    if args.suite:
        if not args.output:
            parser.error("--suite requires --output")
        cases = json.loads(Path(args.suite).read_text(encoding="utf-8"))
        traces = [
            agent.trace(case["case_id"], case["question"], role=case.get("role", "engineer"))
            for case in cases
        ]
        write_trace_jsonl(args.output, traces)
        print(json.dumps({"traces": len(traces), "output": args.output}, ensure_ascii=False))
        return 0
    if not args.question:
        parser.error("question or --suite is required")
    print(json.dumps(result_as_dict(agent.ask(args.question, role=args.role)), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
