from __future__ import annotations

import json
import xml.etree.ElementTree as ET

import pytest

from ragops.ci import github_summary, junit_xml, sarif_report
from ragops.cli import main
from ragops.explain import explain_decision
from ragops.loader import ContractError
from ragops.policy_v2 import GateEvidence, ReleaseDecision, load_release_decision


def _decision() -> ReleaseDecision:
    return ReleaseDecision(
        schema_version="1.0",
        scenario_id="support",
        decision="BLOCK",
        passed=False,
        gates=(
            GateEvidence(
                id="global:citation_coverage:regression",
                metric="citation_coverage",
                scope="global",
                observed=-0.5,
                threshold=0.0,
                comparator=">=",
                passed=False,
                severity="block",
                policy_path="metrics.citation_coverage.max_regression",
                case_ids=("q2",),
            ),
            GateEvidence(
                id="global:latency_ms:maximum",
                metric="latency_ms",
                scope="global",
                observed=80.0,
                threshold=100.0,
                comparator="<=",
                passed=True,
                severity="block",
                policy_path="metrics.latency_ms.maximum",
                case_ids=("q1", "q2"),
            ),
            GateEvidence(
                id="slice:ja:groundedness:minimum",
                metric="groundedness",
                scope="ja",
                observed=0.6,
                threshold=0.8,
                comparator=">=",
                passed=False,
                severity="block",
                policy_path="slices.ja.metrics.groundedness.minimum",
                case_ids=("q2",),
                waived=True,
                waiver_owner="ml-platform",
                waiver_reason="migration window",
                waiver_expires_at="2026-09-01T00:00:00Z",
            ),
        ),
    )


def test_explanation_points_to_policy_cases_and_required_change():
    explanation = explain_decision(_decision())

    assert explanation.decision == "BLOCK"
    failed = explanation.items[0]
    assert failed.policy_path == "metrics.citation_coverage.max_regression"
    assert failed.case_ids == ("q2",)
    assert failed.required_change == 0.5
    assert explanation.items[1].waived is True


def test_junit_marks_blocking_failure_and_waiver_as_skipped():
    root = ET.fromstring(junit_xml(_decision()))

    assert root.attrib == {"name": "ragops: support", "tests": "3", "failures": "1", "skipped": "1"}
    assert len(root.findall(".//failure")) == 1
    assert len(root.findall(".//skipped")) == 1


def test_sarif_and_github_summary_are_bounded_and_escape_untrusted_text():
    decision = _decision()
    sarif = sarif_report(decision)
    summary = github_summary(decision, max_gates=2)

    assert sarif["version"] == "2.1.0"
    assert sarif["runs"][0]["results"][0]["ruleId"] == "global:citation_coverage:regression"
    assert "## RAGOps release gate: BLOCK" in summary
    assert len(summary.splitlines()) < 30


def test_explain_cli_renders_all_ci_formats(tmp_path, monkeypatch, capsys):
    source = tmp_path / "decision.json"
    source.write_text(json.dumps(_decision().to_dict()), encoding="utf-8")

    monkeypatch.setattr("sys.argv", ["ragops", "explain", "--input", str(source)])
    assert main() == 0
    assert json.loads(capsys.readouterr().out)["decision"] == "BLOCK"

    for output_format, suffix in (("junit", "xml"), ("sarif", "json"), ("github", "md")):
        output = tmp_path / f"report.{suffix}"
        monkeypatch.setattr(
            "sys.argv",
            [
                "ragops",
                "ci-render",
                "--input",
                str(source),
                "--format",
                output_format,
                "--output",
                str(output),
            ],
        )
        assert main() == 0
        assert output.stat().st_size > 20


@pytest.mark.parametrize(("field", "value"), [("passed", "false"), ("waived", 0), ("id", 42)])
def test_release_decision_loader_rejects_type_coercion(tmp_path, field, value):
    payload = _decision().to_dict()
    payload["gates"][0][field] = value
    source = tmp_path / "decision.json"
    source.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ContractError):
        load_release_decision(source)


def test_pr_comment_is_sticky_actionable_and_escapes_text():
    from dataclasses import replace

    from ragops.ci import COMMENT_MARKER, pr_comment, render_ci

    decision = _decision()
    comment = pr_comment(decision)

    assert comment.startswith(COMMENT_MARKER)
    assert COMMENT_MARKER == "<!-- ragops-release-gate -->"
    assert "RAGOps release gate: **BLOCK**" in comment
    assert "What to change" in comment
    assert "`global:citation_coverage:regression`" in comment and "`q2`" in comment
    assert "raise to at least 0" in comment
    assert "slice:ja:groundedness" not in comment.split("<details>")[0]  # waived: not an action
    assert "<details>" in comment and "</details>" in comment
    assert render_ci(decision, "comment") == comment

    passing = replace(decision, decision="PASS", passed=True, gates=tuple(
        replace(g, passed=True) for g in decision.gates
    ))
    assert "All gates passed." in pr_comment(passing)

    many = replace(decision, gates=tuple(
        replace(decision.gates[0], id=f"g{i}") for i in range(15)
    ))
    assert "and 5 more failing gates" in pr_comment(many)


def test_action_exposes_comment_input_that_skips_forks():
    from pathlib import Path

    action = Path("action.yml").read_text(encoding="utf-8")
    assert "comment:" in action and "github-token:" in action
    assert "github.event_name == 'pull_request'" in action
    assert 'RAGOPS_COMMENT" != "true"' in action
    assert 'IS_FORK" = "true"' in action
    assert "<!-- ragops-release-gate -->" in action


def test_plain_reason_covers_each_gate_kind():
    from ragops.explain import plain_reason

    regression = plain_reason("global:citation_coverage:regression", "citation_coverage", "global", -0.5, 0.0, ">=")
    assert "dropped by 0.5" in regression and "allows at most 0" in regression
    rising = plain_reason("global:avg_latency_ms:regression", "avg_latency_ms", "global", 30.0, 10.0, "<=")
    assert "rose by 30" in rising
    low = plain_reason("slice:ja:lexical_groundedness:minimum", "lexical_groundedness", "ja", 0.6, 0.8, ">=")
    assert "For the ja slice, the" in low and "below the required minimum of 0.8" in low
    high = plain_reason("global:avg_cost_usd:maximum", "avg_cost_usd", "global", 0.2, 0.1, "<=")
    assert "above the allowed maximum of 0.1" in high
    few = plain_reason("slice:ja:minimum_cases", "case_count", "ja", 2.0, 10.0, ">=")
    assert "only 2 test cases" in few
    unknown = plain_reason("global:my_metric:minimum", "my_metric", "global", 1.0, 2.0, ">=")
    assert "my metric" in unknown


def test_explanation_and_comment_carry_plain_summary():
    from ragops.ci import pr_comment

    decision = _decision()
    first = explain_decision(decision).items[0]
    assert "dropped by 0.5" in first.summary
    assert first.to_dict()["summary"] == first.summary
    assert "dropped by 0.5" in pr_comment(decision)


def test_explanation_keeps_waiver_details_and_schema_fields():
    explanation = explain_decision(_decision())
    waived = explanation.items[1]
    assert waived.waiver == {"owner": "ml-platform", "reason": "migration window", "expires_at": "2026-09-01T00:00:00Z"}
    assert explanation.items[0].waiver is None
    data = explanation.to_dict()
    assert data["schema_version"] == "1.0" and data["scenario_id"] == "support" and data["decision"] == "BLOCK"
    assert set(data["items"][1]["waiver"]) == {"owner", "reason", "expires_at"}


def test_plain_reason_exact_wording():
    from ragops.explain import plain_reason

    assert plain_reason("global:citation_coverage:regression", "citation_coverage", "global", -0.5, 0.0, ">=") == (
        "Overall, the share of answers that cite a source dropped by 0.5 compared with the baseline; "
        "the policy allows at most 0."
    )
    assert plain_reason("slice:ja:minimum_cases", "case_count", "ja", 2.0, 10.0, ">=") == (
        "The ja slice has only 2 test cases but at least 10 are needed, so its result is not trustworthy yet. "
        "Add cases or lower the minimum."
    )
    assert plain_reason("global:avg_cost_usd:maximum", "avg_cost_usd", "global", 0.2, 0.1, "<=").startswith(
        "Overall, the average cost per answer (USD) is 0.2"
    )
