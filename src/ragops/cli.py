from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from ragops import __version__
from ragops.adapter_sdk import AdapterContext, discover_adapters
from ragops.adapters.external_metrics import (
    load_external_metric_evaluator,
    validate_external_metric_pair,
)
from ragops.adapters.import_profiles import convert_import
from ragops.adapters.otel_genai import otel_spans_to_trace_graph
from ragops.adapters.repeated_runs import (
    CommandMetricAdapter,
    collect_repeated_runs,
    load_repeated_run_plan,
    load_resume_bundle,
    write_replay_bundle,
)
from ragops.adapters.signing import sign_baseline_manifest, verify_baseline_signature
from ragops.baseline import (
    create_baseline_manifest,
    load_baseline_manifest,
    verify_baseline_manifest,
    write_baseline_manifest,
)
from ragops.benchmarks import scenario_summary
from ragops.calibration import calibrate_evaluator, load_calibration_set
from ragops.ci import render_ci
from ragops.cli_helpers import (
    _evaluators_from_names,
    _named_csv_values,
    _named_int_values,
)
from ragops.cli_parser import build_parser
from ragops.config import (
    load_evaluation_policy,
    load_evaluator_drift_policy,
    load_regression_policy,
    load_sequential_policy,
    load_statistical_policy,
)
from ragops.contracts import diff_contract, migrate_contract, validate_contract
from ragops.control_plane import ControlPlane
from ragops.datasets import (
    create_dataset_manifest,
    diff_dataset_manifests,
    load_dataset_manifest,
    validate_dataset_manifest,
    write_dataset_manifest,
)
from ragops.demo import write_demo
from ragops.drift import detect_evaluator_drift
from ragops.engine import compare, evaluate
from ragops.evidence import create_evidence_bundle, verify_evidence_bundle
from ragops.explain import explain_decision
from ragops.explorer import explorer_html
from ragops.governance import GovernanceStore
from ragops.init_project import init_project
from ragops.loader import ContractError, load_responses, load_scenario
from ragops.models import ComparisonReport, EvaluationReport, SequentialComparisonReport
from ragops.pilot import (
    PilotContractError,
    load_pilot_economics,
    load_pilot_manifest,
    load_pilot_observations,
    pilot_markdown,
    summarize_pilot,
    write_pilot_scaffold,
)
from ragops.policy_suggest import suggest_release_policy
from ragops.policy_v2 import apply_release_policy, load_release_decision, load_release_policy_v2
from ragops.provenance import diagnose_provenance
from ragops.reporters import (
    comparison_html,
    comparison_markdown,
    evaluation_markdown,
    evaluator_drift_markdown,
    sequential_comparison_markdown,
    statistical_comparison_markdown,
)
from ragops.sequential import compare_replay_bundles_sequentially
from ragops.statistical import compare_replay_bundles, load_replay_bundle
from ragops.store import ExperimentStore
from ragops.trace_graph import evaluate_trace_graph, load_trace_expectation, load_trace_graph
from ragops.traces import load_trace_jsonl
from ragops.usage import UsageContractError, record_local_usage, summarize_local_usage


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "contract":
        try:
            if args.contract_command == "diff":
                payload = diff_contract(args.kind, args.from_version, args.to_version).to_dict()
            else:
                source = Path(args.input)
                data = json.loads(source.read_text(encoding="utf-8"))
                if args.contract_command == "validate":
                    payload = validate_contract(data, args.kind).to_dict()
                else:
                    output = Path(args.output)
                    if source.resolve() == output.resolve():
                        raise SystemExit("contract input and output must differ")
                    migrated = migrate_contract(
                        data,
                        args.kind,
                        args.from_version,
                        args.to_version,
                        question=args.question,
                    )
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_text(
                        json.dumps(migrated, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8",
                    )
                    payload = {
                        "kind": args.kind,
                        "from_version": args.from_version,
                        "to_version": args.to_version,
                        "output": str(output),
                    }
        except (ContractError, OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise SystemExit(f"contract error: {exc}") from exc
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    if args.command == "evidence":
        try:
            if args.evidence_command == "verify":
                manifest = verify_evidence_bundle(args.bundle)
                payload = {"verified": True, **manifest.to_dict()}
            else:
                artifact_paths = {}
                for value in args.artifact:
                    if "=" not in value:
                        raise ContractError("Evidence artifacts must use NAME=PATH")
                    name, raw_path = value.split("=", 1)
                    if name in artifact_paths:
                        raise ContractError(f"Duplicate evidence artifact name: {name}")
                    artifact_paths[name] = raw_path
                created_at = args.created_at or datetime.now(UTC).isoformat().replace("+00:00", "Z")
                metadata = json.loads(args.metadata_json)
                manifest = create_evidence_bundle(
                    args.bundle,
                    artifact_paths,
                    args.decision,
                    tuple(args.limitation),
                    created_at,
                    metadata,
                )
                payload = manifest.to_dict()
        except (ContractError, FileExistsError, OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise SystemExit(f"evidence error: {exc}") from exc
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    if args.command == "gate-v2":
        try:
            scenario = load_scenario(args.scenario)
            release_report = apply_release_policy(
                load_release_policy_v2(args.policy),
                evaluate(scenario, load_responses(args.baseline)),
                evaluate(scenario, load_responses(args.candidate)),
                scenario,
                now=args.now or datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            )
        except (ContractError, OSError, ValueError) as exc:
            raise SystemExit(f"release policy error: {exc}") from exc
        rendered = json.dumps(release_report.to_dict(), ensure_ascii=False, indent=2) + "\n"
        if args.output:
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 2 if release_report.decision == "BLOCK" else 0
    if args.command == "policy-suggest":
        try:
            scenario = load_scenario(args.scenario)
            rendered = suggest_release_policy(
                scenario,
                evaluate(scenario, load_responses(args.baseline)),
                margin=args.margin,
                min_cases=args.min_cases,
            )
        except (ContractError, OSError, ValueError) as exc:
            raise SystemExit(f"policy suggestion error: {exc}") from exc
        if args.output:
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 0
    if args.command == "calibrate":
        try:
            calibration_set = load_calibration_set(args.input)
            calibration_report = calibrate_evaluator(
                calibration_set.evaluator,
                calibration_set.records,
                calibration_set.policy,
            )
        except (ContractError, OSError, ValueError) as exc:
            raise SystemExit(f"calibration error: {exc}") from exc
        rendered = json.dumps(calibration_report.to_dict(), ensure_ascii=False, indent=2) + "\n"
        if args.output:
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0 if calibration_report.decision == "PASS" else 2
    if args.command == "trace":
        try:
            if args.trace_command == "convert-otel":
                raw_spans = json.loads(Path(args.input).read_text(encoding="utf-8"))
                graph = otel_spans_to_trace_graph(raw_spans)
                output = Path(args.output)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(
                    json.dumps(graph.to_dict(), ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                payload = {"converted": True, "trace_id": graph.trace_id, "output": str(output)}
                exit_code = 0
            else:
                graph_report = evaluate_trace_graph(
                    load_trace_graph(args.trace), load_trace_expectation(args.expectation)
                )
                payload = graph_report.to_dict()
                rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
                if args.output:
                    output = Path(args.output)
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_text(rendered, encoding="utf-8")
                exit_code = 0 if graph_report.decision == "PASS" else 2
        except (ContractError, OSError, json.JSONDecodeError, ValueError) as exc:
            raise SystemExit(f"trace error: {exc}") from exc
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return exit_code
    if args.command == "dataset":
        try:
            if args.dataset_command == "create":
                scenario = load_scenario(args.scenario)
                splits = _named_csv_values(args.split, "dataset split")
                cases = tuple(
                    {
                        "id": item.id,
                        "question": item.question,
                        "evidence": list(item.evidence),
                        "required_citation_ids": list(item.required_citation_ids),
                        "category": item.category,
                        "severity": item.severity,
                        "language": item.language,
                        "tags": list(item.tags),
                        "source": f"scenario:{scenario.id}",
                        "reviewed": args.reviewed,
                    }
                    for item in scenario.cases
                )
                dataset_manifest = create_dataset_manifest(
                    args.dataset_id,
                    args.version,
                    cases,
                    splits=splits,
                    source_classification=args.source_classification,
                    owners=tuple(args.owner),
                )
                write_dataset_manifest(args.output, dataset_manifest)
                payload = dataset_manifest.to_dict()
                exit_code = 0
            elif args.dataset_command == "validate":
                minimum_slices = _named_int_values(args.minimum_slice, "dataset minimum slice")
                dataset_manifest = load_dataset_manifest(args.manifest)
                issues = validate_dataset_manifest(dataset_manifest, minimum_slice_counts=minimum_slices)
                payload = {"valid": not issues, "issues": [item.to_dict() for item in issues]}
                exit_code = 0 if not issues else 2
            else:
                difference = diff_dataset_manifests(
                    load_dataset_manifest(args.before), load_dataset_manifest(args.after)
                )
                payload = difference.to_dict()
                exit_code = 0
        except (ContractError, OSError, ValueError) as exc:
            raise SystemExit(f"dataset error: {exc}") from exc
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return exit_code
    if args.command in {"explain", "ci-render"}:
        try:
            decision = load_release_decision(args.input)
            if args.command == "explain":
                rendered = json.dumps(explain_decision(decision).to_dict(), ensure_ascii=False, indent=2) + "\n"
            else:
                rendered = render_ci(decision, args.format)
            if args.output:
                output = Path(args.output)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(rendered, encoding="utf-8")
            else:
                print(rendered, end="")
        except (ContractError, OSError, ValueError) as exc:
            raise SystemExit(f"release explanation error: {exc}") from exc
        return 0
    if args.command == "adapter":
        try:
            if args.adapter_command == "list":
                payload = {"adapters": [item.to_dict() for item in discover_adapters()]}
            else:
                raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
                converted = convert_import(
                    args.profile, raw, AdapterContext(case_ids=tuple(args.case_id))
                )
                payload = converted.to_dict()
                output = Path(args.output)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
        except (ContractError, OSError, json.JSONDecodeError, ValueError) as exc:
            raise SystemExit(f"adapter error: {exc}") from exc
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    if args.command == "governance":
        try:
            governance_store = GovernanceStore(args.store)
            if args.governance_command == "register":
                public = json.loads(Path(args.metadata).read_text(encoding="utf-8"))
                blinded = (
                    json.loads(Path(args.blinded_metadata).read_text(encoding="utf-8"))
                    if args.blinded_metadata else {}
                )
                governance_store.register_artifact(
                    args.artifact_id, kind=args.kind, digest=args.digest,
                    public_metadata=public, blinded_metadata=blinded, actor=args.actor,
                )
                payload = governance_store.get_artifact(args.artifact_id)
            elif args.governance_command == "transition":
                governance_store.transition(args.artifact_id, args.state, actor=args.actor)
                payload = governance_store.get_artifact(args.artifact_id)
            elif args.governance_command == "review":
                governance_store.record_review(
                    args.artifact_id, reviewer=args.reviewer, verdict=args.verdict, note=args.note
                )
                payload = {"recorded": True}
            elif args.governance_command == "queue":
                payload = {"artifacts": governance_store.review_queue(args.reviewer)}
            else:
                payload = {"events": governance_store.audit_events(args.artifact_id)}
        except (KeyError, ValueError, OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"governance error: {exc}") from exc
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    if args.command == "serve":
        if not 1 <= args.port <= 65535:
            raise SystemExit("serve error: port must be between 1 and 65535")
        try:
            import uvicorn
        except ImportError as exc:
            raise SystemExit("serve requires the API extra: pip install 'ragops[api]'") from exc
        uvicorn.run("ragops.api.main:app", host=args.host, port=args.port, reload=args.reload)
        return 0
    if args.command == "demo":
        try:
            summary = write_demo(
                args.output, force=args.force, scenario_id=args.scenario, profile=args.profile
            )
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
    if args.command == "init":
        try:
            outcome = init_project(
                args.source,
                args.output,
                scenario_id=args.scenario_id,
                source_format=args.source_format,
                candidate=args.candidate,
            )
        except ContractError as exc:
            raise SystemExit(f"contract error: {exc}") from exc
        print(json.dumps(outcome.to_dict(), ensure_ascii=False, indent=2))
        print(
            f"\nNext: ragops evaluate --scenario {outcome.files[0]} --responses {outcome.files[1]}"
            " --evaluator strict_grounding --format markdown",
            file=sys.stderr,
        )
        return 0
    if args.command == "pilot-init":
        try:
            created = write_pilot_scaffold(args.output, args.pilot_id, args.label)
        except PilotContractError as exc:
            raise SystemExit(f"pilot contract error: {exc}") from exc
        print(json.dumps({"created": [str(path) for path in created]}, indent=2))
        return 0
    if args.command == "pilot-report":
        try:
            pilot_summary = summarize_pilot(
                load_pilot_manifest(args.manifest),
                load_pilot_observations(args.observations),
                load_pilot_economics(args.economics) if args.economics else None,
            )
        except PilotContractError as exc:
            raise SystemExit(f"pilot contract error: {exc}") from exc
        rendered = (
            json.dumps(pilot_summary.to_dict(), ensure_ascii=False, indent=2)
            if args.format == "json"
            else pilot_markdown(pilot_summary)
        )
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered.rstrip() + "\n", encoding="utf-8")
        else:
            print(rendered.rstrip())
        return 0
    if args.command == "usage-report":
        try:
            usage_summary = summarize_local_usage(args.events)
        except UsageContractError as exc:
            raise SystemExit(f"usage contract error: {exc}") from exc
        rendered = json.dumps(usage_summary, ensure_ascii=False, indent=2)
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered + "\n", encoding="utf-8")
        else:
            print(rendered)
        return 0
    if args.command == "compare-runs":
        try:
            statistical_report = compare_replay_bundles(
                load_replay_bundle(args.baseline_bundle),
                load_replay_bundle(args.candidate_bundle),
                load_statistical_policy(args.policy),
            )
        except (ContractError, ValueError) as exc:
            raise SystemExit(f"contract error: {exc}") from exc
        rendered = (
            json.dumps(statistical_report.to_dict(), ensure_ascii=False, indent=2)
            if args.format == "json"
            else statistical_comparison_markdown(statistical_report)
        )
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered.rstrip() + "\n", encoding="utf-8")
        else:
            print(rendered.rstrip())
        return 0 if statistical_report.passed else 2
    if args.command == "collect-runs":
        command = tuple(
            args.runner_command[1:]
            if args.runner_command[:1] == ["--"]
            else args.runner_command
        )
        try:
            plan = load_repeated_run_plan(args.plan)
            existing = load_resume_bundle(args.output, resume=args.resume)
            if bool(args.baseline_bundle) != bool(args.sequential_policy):
                raise ContractError(
                    "Sequential collection requires both --baseline-bundle and "
                    "--sequential-policy"
                )
            sequential_reports: list[SequentialComparisonReport] = []
            stop_when = None
            if args.baseline_bundle:
                sequential_baseline = load_replay_bundle(args.baseline_bundle)
                sequential_policy = load_sequential_policy(args.sequential_policy)
                if plan.repeats != sequential_policy.maximum_repeats:
                    raise ContractError(
                        "Repeated-run plan repeats must equal sequential maximum_repeats"
                    )

                def stop_when(current):
                    if {record.case_id for record in current.records} != set(plan.case_ids):
                        return False
                    decision = compare_replay_bundles_sequentially(
                        sequential_baseline,
                        current,
                        sequential_policy,
                    )
                    sequential_reports[:] = [decision]
                    return decision.decision in {"pass", "block"}

            bundle = collect_repeated_runs(
                plan,
                CommandMetricAdapter(command, timeout_seconds=args.timeout_seconds),
                existing=existing,
                checkpoint=lambda current: write_replay_bundle(args.output, current),
                stop_when=stop_when,
            )
            write_replay_bundle(args.output, bundle)
            if sequential_reports:
                report_path = Path(
                    args.sequential_report or f"{args.output}.sequential.json"
                )
                report_path.parent.mkdir(parents=True, exist_ok=True)
                report_path.write_text(
                    json.dumps(
                        sequential_reports[-1].to_dict(), ensure_ascii=False, indent=2
                    )
                    + "\n",
                    encoding="utf-8",
                )
        except (ContractError, ValueError) as exc:
            raise SystemExit(f"collection error: {exc}") from exc
        print(
            json.dumps(
                {
                    "output": str(args.output),
                    "cases": len(plan.case_ids),
                    "repeats": plan.repeats,
                    "observations": len(bundle.records),
                    "sequential_decision": (
                        sequential_reports[-1].decision if sequential_reports else None
                    ),
                },
                ensure_ascii=False,
            )
        )
        return (
            2
            if sequential_reports and sequential_reports[-1].decision != "pass"
            else 0
        )
    if args.command == "detect-evaluator-drift":
        try:
            drift_report = detect_evaluator_drift(
                load_replay_bundle(args.reference_bundle),
                load_replay_bundle(args.current_bundle),
                load_evaluator_drift_policy(args.policy),
            )
        except (ContractError, ValueError) as exc:
            raise SystemExit(f"drift contract error: {exc}") from exc
        rendered = (
            json.dumps(drift_report.to_dict(), ensure_ascii=False, indent=2)
            if args.format == "json"
            else evaluator_drift_markdown(drift_report)
        )
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered.rstrip() + "\n", encoding="utf-8")
        else:
            print(rendered.rstrip())
        return 0 if drift_report.passed else 2
    if args.command == "compare-sequential":
        try:
            sequential_report = compare_replay_bundles_sequentially(
                load_replay_bundle(args.baseline_bundle),
                load_replay_bundle(args.candidate_bundle),
                load_sequential_policy(args.policy),
            )
        except (ContractError, ValueError) as exc:
            raise SystemExit(f"sequential contract error: {exc}") from exc
        rendered = (
            json.dumps(sequential_report.to_dict(), ensure_ascii=False, indent=2)
            if args.format == "json"
            else sequential_comparison_markdown(sequential_report)
        )
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered.rstrip() + "\n", encoding="utf-8")
        else:
            print(rendered.rstrip())
        return 0 if sequential_report.passed else 2
    if args.command == "baseline-create":
        try:
            baseline_manifest = create_baseline_manifest(
                args.bundle,
                args.policy,
                owner=args.owner,
                accepted_at=args.accepted_at,
            )
            write_baseline_manifest(args.output, baseline_manifest)
        except ContractError as exc:
            raise SystemExit(f"baseline contract error: {exc}") from exc
        print(json.dumps({"manifest": str(args.output), "verified": True}))
        return 0
    if args.command == "baseline-sign":
        try:
            load_baseline_manifest(args.manifest)
            sign_baseline_manifest(args.manifest, args.key, args.output)
        except ContractError as exc:
            raise SystemExit(f"baseline signing error: {exc}") from exc
        print(json.dumps({"signature": str(args.output)}))
        return 0
    if args.command == "baseline-verify":
        signature_options = (args.signature, args.allowed_signers, args.identity)
        if any(signature_options) and not all(signature_options):
            raise SystemExit(
                "baseline contract error: signature verification requires --signature, "
                "--allowed-signers, and --identity"
            )
        try:
            baseline_manifest = load_baseline_manifest(args.manifest)
            verify_baseline_manifest(baseline_manifest, args.bundle, args.policy)
            if args.signature:
                verify_baseline_signature(
                    args.manifest,
                    args.signature,
                    args.allowed_signers,
                    args.identity,
                )
        except ContractError as exc:
            raise SystemExit(f"baseline verification error: {exc}") from exc
        print(
            json.dumps(
                {
                    "verified": True,
                    "signature_verified": bool(args.signature),
                    "owner": baseline_manifest.acceptance.owner,
                }
            )
        )
        return 0
    if args.command == "diagnose-provenance":
        try:
            diagnosis = diagnose_provenance(
                load_replay_bundle(args.reference_bundle),
                load_replay_bundle(args.current_bundle),
            )
        except ContractError as exc:
            raise SystemExit(f"provenance contract error: {exc}") from exc
        print(json.dumps(diagnosis.to_dict(), ensure_ascii=False, indent=2))
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
    report: EvaluationReport | ComparisonReport
    try:
        scenario = load_scenario(args.scenario)
        if args.command == "evaluate":
            evaluators = _evaluators_from_names(
                args.evaluator,
                answer_length_limit=args.answer_length_limit,
                semantic_command=args.semantic_command,
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
                semantic_command=args.semantic_command,
            )
            if args.baseline_external_metrics:
                baseline_external = load_external_metric_evaluator(
                    args.baseline_external_metrics, scenario
                )
                candidate_external = load_external_metric_evaluator(
                    args.candidate_external_metrics, scenario
                )
                validate_external_metric_pair(baseline_external, candidate_external)
            baseline_responses = (
                load_trace_jsonl(args.baseline_traces)
                if args.baseline_traces
                else load_responses(args.baseline)
            )
            candidate_responses = (
                load_trace_jsonl(args.candidate_traces)
                if args.candidate_traces
                else load_responses(args.candidate)
            )
            report = compare(
                scenario,
                baseline_responses,
                candidate_responses,
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
    elif isinstance(report, EvaluationReport):
        rendered = evaluation_markdown(report)
    elif args.format == "html":
        rendered = comparison_html(report)
    elif args.format == "explorer":
        rendered = explorer_html(scenario, baseline_responses, candidate_responses, report)
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


def _usage_command(arguments: list[str]) -> str:
    if not arguments or arguments[0] in {"-h", "--help"}:
        return "help"
    if arguments[0] == "--version":
        return "version"
    candidate = arguments[0]
    for action in build_parser()._actions:
        if isinstance(action, argparse._SubParsersAction):
            return candidate if candidate in action.choices else "unknown"
    return "unknown"


def cli_entrypoint() -> int:
    exit_code = 1
    try:
        exit_code = main()
        return exit_code
    except SystemExit as exc:
        if isinstance(exc.code, int) and not isinstance(exc.code, bool):
            exit_code = exc.code
        elif exc.code is None:
            exit_code = 0
        raise
    finally:
        usage_log = os.environ.get("RAGOPS_USAGE_LOG")
        if usage_log:
            try:
                record_local_usage(
                    usage_log,
                    ragops_version=__version__,
                    command=_usage_command(sys.argv[1:]),
                    exit_code=exit_code if 0 <= exit_code <= 255 else 1,
                )
            except (OSError, UsageContractError) as exc:
                print(f"usage log warning: {exc}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(cli_entrypoint())
