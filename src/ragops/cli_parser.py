"""Argument parser for the ``ragops`` command line."""

from __future__ import annotations

import argparse

from ragops import __version__
from ragops.demo import DEFAULT_DEMO_SCENARIO, DEMO_BUNDLES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ragops")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    contract_parser = commands.add_parser("contract", help="Validate and migrate contracts")
    contract_commands = contract_parser.add_subparsers(dest="contract_command", required=True)
    contract_validate = contract_commands.add_parser("validate", help="Validate a JSON contract")
    contract_validate.add_argument("--kind", choices=("auto", "scenario", "trace"), default="auto")
    contract_validate.add_argument("--input", required=True)
    contract_diff = contract_commands.add_parser("diff", help="Compare contract versions")
    contract_diff.add_argument("--kind", choices=("scenario", "trace"), required=True)
    contract_diff.add_argument("--from", dest="from_version", required=True)
    contract_diff.add_argument("--to", dest="to_version", required=True)
    contract_migrate = contract_commands.add_parser("migrate", help="Migrate a JSON contract")
    contract_migrate.add_argument("--kind", choices=("scenario", "trace"), required=True)
    contract_migrate.add_argument("--from", dest="from_version", required=True)
    contract_migrate.add_argument("--to", dest="to_version", required=True)
    contract_migrate.add_argument("--input", required=True)
    contract_migrate.add_argument("--output", required=True)
    contract_migrate.add_argument("--question", default="")
    evidence_parser = commands.add_parser("evidence", help="Create and verify evidence bundles")
    evidence_commands = evidence_parser.add_subparsers(dest="evidence_command", required=True)
    evidence_create = evidence_commands.add_parser("create", help="Create an evidence bundle")
    evidence_create.add_argument("--bundle", required=True)
    evidence_create.add_argument("--decision", choices=("PASS", "WARN", "BLOCK"), required=True)
    evidence_create.add_argument("--artifact", action="append", required=True, metavar="NAME=PATH")
    evidence_create.add_argument("--limitation", action="append", required=True)
    evidence_create.add_argument("--created-at")
    evidence_create.add_argument("--metadata-json", default="{}")
    evidence_verify = evidence_commands.add_parser("verify", help="Verify an evidence bundle")
    evidence_verify.add_argument("--bundle", required=True)
    gate_v2 = commands.add_parser("gate-v2", help="Apply slice-aware release policy v2")
    gate_v2.add_argument("--scenario", required=True)
    gate_v2.add_argument("--baseline", required=True)
    gate_v2.add_argument("--candidate", required=True)
    gate_v2.add_argument("--policy", required=True)
    gate_v2.add_argument("--now")
    gate_v2.add_argument("--output")
    policy_suggest = commands.add_parser(
        "policy-suggest", help="Generate a slice-aware release policy from an accepted baseline"
    )
    policy_suggest.add_argument("--scenario", required=True)
    policy_suggest.add_argument("--baseline", required=True)
    policy_suggest.add_argument("--margin", type=float, default=0.05)
    policy_suggest.add_argument("--min-cases", type=int, default=3)
    policy_suggest.add_argument("--output")
    calibrate = commands.add_parser("calibrate", help="Calibrate an evaluator against human labels")
    calibrate.add_argument("--input", required=True)
    calibrate.add_argument("--output")
    trace_parser = commands.add_parser("trace", help="Convert and evaluate agent trace graphs")
    trace_commands = trace_parser.add_subparsers(dest="trace_command", required=True)
    trace_evaluate = trace_commands.add_parser("evaluate", help="Evaluate a trace graph")
    trace_evaluate.add_argument("--trace", required=True)
    trace_evaluate.add_argument("--expectation", required=True)
    trace_evaluate.add_argument("--output")
    trace_convert = trace_commands.add_parser("convert-otel", help="Convert OpenTelemetry JSON")
    trace_convert.add_argument("--input", required=True)
    trace_convert.add_argument("--output", required=True)
    dataset_parser = commands.add_parser("dataset", help="Manage benchmark dataset manifests")
    dataset_commands = dataset_parser.add_subparsers(dest="dataset_command", required=True)
    dataset_create = dataset_commands.add_parser("create", help="Create a dataset manifest")
    dataset_create.add_argument("--scenario", required=True)
    dataset_create.add_argument("--dataset-id", required=True)
    dataset_create.add_argument("--version", required=True)
    dataset_create.add_argument(
        "--source-classification", choices=("synthetic", "public", "production-derived"), required=True
    )
    dataset_create.add_argument("--owner", action="append", required=True)
    dataset_create.add_argument("--split", action="append", required=True, metavar="NAME=ID,ID")
    dataset_create.add_argument("--reviewed", action="store_true")
    dataset_create.add_argument("--output", required=True)
    dataset_validate = dataset_commands.add_parser("validate", help="Validate a dataset manifest")
    dataset_validate.add_argument("--manifest", required=True)
    dataset_validate.add_argument("--minimum-slice", action="append", default=[], metavar="SELECTOR=COUNT")
    dataset_diff = dataset_commands.add_parser("diff", help="Diff dataset manifests")
    dataset_diff.add_argument("--before", required=True)
    dataset_diff.add_argument("--after", required=True)
    explain_parser = commands.add_parser("explain", help="Explain failed release gates")
    explain_parser.add_argument("--input", required=True)
    explain_parser.add_argument("--output")
    ci_render = commands.add_parser("ci-render", help="Render release decisions for CI systems")
    ci_render.add_argument("--input", required=True)
    ci_render.add_argument("--format", choices=("junit", "sarif", "github", "comment"), required=True)
    ci_render.add_argument("--output", required=True)
    adapter_parser = commands.add_parser("adapter", help="Discover and run portable import adapters")
    adapter_commands = adapter_parser.add_subparsers(dest="adapter_command", required=True)
    adapter_commands.add_parser("list", help="List built-in and installed adapters")
    adapter_convert = adapter_commands.add_parser("convert", help="Convert vendor JSON to a portable envelope")
    adapter_convert.add_argument("--profile", required=True)
    adapter_convert.add_argument("--input", required=True)
    adapter_convert.add_argument("--case-id", action="append", default=[])
    adapter_convert.add_argument("--output", required=True)
    governance = commands.add_parser("governance", help="Manage governed artifacts and blind reviews")
    governance_commands = governance.add_subparsers(dest="governance_command", required=True)
    governance_register = governance_commands.add_parser("register")
    governance_register.add_argument("--store", required=True)
    governance_register.add_argument("--artifact-id", required=True)
    governance_register.add_argument("--kind", required=True)
    governance_register.add_argument("--digest", required=True)
    governance_register.add_argument("--metadata", required=True)
    governance_register.add_argument("--blinded-metadata")
    governance_register.add_argument("--actor", required=True)
    governance_transition = governance_commands.add_parser("transition")
    governance_transition.add_argument("--store", required=True)
    governance_transition.add_argument("--artifact-id", required=True)
    governance_transition.add_argument("--state", choices=("reviewed", "accepted", "superseded"), required=True)
    governance_transition.add_argument("--actor", required=True)
    governance_review = governance_commands.add_parser("review")
    governance_review.add_argument("--store", required=True)
    governance_review.add_argument("--artifact-id", required=True)
    governance_review.add_argument("--reviewer", required=True)
    governance_review.add_argument("--verdict", choices=("approve", "block"), required=True)
    governance_review.add_argument("--note", default="")
    governance_queue = governance_commands.add_parser("queue")
    governance_queue.add_argument("--store", required=True)
    governance_queue.add_argument("--reviewer", required=True)
    governance_audit = governance_commands.add_parser("audit")
    governance_audit.add_argument("--store", required=True)
    governance_audit.add_argument("--artifact-id")
    serve = commands.add_parser("serve", help="Run the optional local API and workbench")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--reload", action="store_true")
    demo_parser = commands.add_parser("demo", help="Generate a credential-free release-gate demo")
    demo_parser.add_argument("--output", default="ragops-demo")
    demo_parser.add_argument(
        "--scenario",
        choices=tuple(sorted(DEMO_BUNDLES)),
        default=DEFAULT_DEMO_SCENARIO,
        help="Credential-free workflow scenario to generate",
    )
    demo_parser.add_argument(
        "--profile", choices=("executive", "engineer", "auditor"), default="engineer"
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
            "strict_grounding",
            "semantic_grounding",
            "answer_length_budget",
            "source_freshness",
            "abstention_contract",
        ),
        default=[],
    )
    evaluate_parser.add_argument(
        "--semantic-command",
        help="Command (no shell) for semantic_grounding; reads claim JSON on stdin",
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
    compare_parser.add_argument(
        "--format", choices=("json", "markdown", "html", "explorer"), default="markdown"
    )
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
            "strict_grounding",
            "semantic_grounding",
            "answer_length_budget",
            "source_freshness",
            "abstention_contract",
        ),
        default=[],
    )
    compare_parser.add_argument(
        "--semantic-command",
        help="Command (no shell) for semantic_grounding; reads claim JSON on stdin",
    )
    compare_parser.add_argument(
        "--answer-length-limit",
        type=int,
        default=500,
        help="Unicode code-point limit for answer_length_budget (default: 500)",
    )
    compare_runs_parser = commands.add_parser(
        "compare-runs",
        help="Compare repeated metric observations with uncertainty-aware gates",
    )
    compare_runs_parser.add_argument("--baseline-bundle", required=True)
    compare_runs_parser.add_argument("--candidate-bundle", required=True)
    compare_runs_parser.add_argument("--policy", required=True)
    compare_runs_parser.add_argument("--output")
    compare_runs_parser.add_argument(
        "--format", choices=("json", "markdown"), default="markdown"
    )
    collect_runs_parser = commands.add_parser(
        "collect-runs",
        help="Collect a resumable replay bundle from an explicit metric command",
    )
    collect_runs_parser.add_argument("--plan", required=True)
    collect_runs_parser.add_argument("--output", required=True)
    collect_runs_parser.add_argument("--resume", action="store_true")
    collect_runs_parser.add_argument("--timeout-seconds", type=float, default=60.0)
    collect_runs_parser.add_argument("--baseline-bundle")
    collect_runs_parser.add_argument("--sequential-policy")
    collect_runs_parser.add_argument("--sequential-report")
    collect_runs_parser.add_argument(
        "--command",
        dest="runner_command",
        nargs=argparse.REMAINDER,
        required=True,
        help="Command to run; receives RAGOPS_CASE_ID and RAGOPS_REPEAT_ID",
    )
    drift_parser = commands.add_parser(
        "detect-evaluator-drift",
        help="Compare frozen anchors across evaluator versions",
    )
    drift_parser.add_argument("--reference-bundle", required=True)
    drift_parser.add_argument("--current-bundle", required=True)
    drift_parser.add_argument("--policy", required=True)
    drift_parser.add_argument("--output")
    drift_parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    sequential_parser = commands.add_parser(
        "compare-sequential",
        help="Apply predeclared sequential looks to repeated metric bundles",
    )
    sequential_parser.add_argument("--baseline-bundle", required=True)
    sequential_parser.add_argument("--candidate-bundle", required=True)
    sequential_parser.add_argument("--policy", required=True)
    sequential_parser.add_argument("--output")
    sequential_parser.add_argument(
        "--format", choices=("json", "markdown"), default="markdown"
    )
    baseline_create = commands.add_parser(
        "baseline-create", help="Create a content-addressed accepted-baseline manifest"
    )
    baseline_create.add_argument("--bundle", required=True)
    baseline_create.add_argument("--policy", required=True)
    baseline_create.add_argument("--owner", required=True)
    baseline_create.add_argument("--accepted-at", required=True)
    baseline_create.add_argument("--output", required=True)
    baseline_sign = commands.add_parser(
        "baseline-sign", help="Sign a baseline manifest with an SSH key"
    )
    baseline_sign.add_argument("--manifest", required=True)
    baseline_sign.add_argument("--key", required=True)
    baseline_sign.add_argument("--output", required=True)
    baseline_verify = commands.add_parser(
        "baseline-verify", help="Verify baseline integrity and optional SSH signature"
    )
    baseline_verify.add_argument("--manifest", required=True)
    baseline_verify.add_argument("--bundle", required=True)
    baseline_verify.add_argument("--policy", required=True)
    baseline_verify.add_argument("--signature")
    baseline_verify.add_argument("--allowed-signers")
    baseline_verify.add_argument("--identity")
    provenance_parser = commands.add_parser(
        "diagnose-provenance",
        help="Classify model, evaluator, dataset, and infrastructure changes",
    )
    provenance_parser.add_argument("--reference-bundle", required=True)
    provenance_parser.add_argument("--current-bundle", required=True)
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
    init_parser = commands.add_parser(
        "init", help="Create a first release-gate scenario from your own RAG logs"
    )
    init_parser.add_argument("--from", dest="source", required=True, help="JSON/JSONL file or directory")
    init_parser.add_argument("--output", required=True)
    init_parser.add_argument("--scenario-id", default="my-rag")
    init_parser.add_argument(
        "--candidate",
        help="Logs of a later run of the same questions: also writes candidate.json and a comparison",
    )
    init_parser.add_argument(
        "--source-format",
        choices=("generic", "langfuse", "openai", "anthropic"),
        default="generic",
        help="Shape of the logs: a Langfuse trace export, OpenAI or Anthropic request/response logs",
    )
    pilot_init_parser = commands.add_parser(
        "pilot-init", help="Create blank design-partner pilot files that fail closed"
    )
    pilot_init_parser.add_argument("--output", required=True)
    pilot_init_parser.add_argument("--pilot-id", required=True)
    pilot_init_parser.add_argument("--label", required=True)
    pilot_parser = commands.add_parser(
        "pilot-report", help="Summarize design-partner adoption and ROI evidence"
    )
    pilot_parser.add_argument("--manifest", required=True)
    pilot_parser.add_argument("--observations", required=True)
    pilot_parser.add_argument("--economics")
    pilot_parser.add_argument("--output")
    pilot_parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    usage_parser = commands.add_parser(
        "usage-report", help="Summarize explicitly enabled local CLI usage events"
    )
    usage_parser.add_argument("--events", required=True)
    usage_parser.add_argument("--output")
    usage_parser.add_argument("--format", choices=("json",), default="json")
    return parser
