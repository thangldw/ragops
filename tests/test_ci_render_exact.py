"""Exact-output tests for the CI renderers (found weak by mutation testing)."""

import json
import xml.etree.ElementTree as ET

import pytest

from ragops.ci import COMMENT_MARKER, github_summary, junit_xml, pr_comment, render_ci, sarif_report
from ragops.policy_v2 import GateEvidence, ReleaseDecision


def _gate(gate_id, severity="block", passed=False, waived=False, observed=0.5, threshold=0.8, comparator=">=", cases=("q1",)):
    return GateEvidence(
        id=gate_id,
        metric=gate_id.split(":")[-2] if gate_id.count(":") > 1 else gate_id,
        scope="global",
        observed=observed,
        threshold=threshold,
        comparator=comparator,
        passed=passed,
        severity=severity,
        policy_path=f"metrics.{gate_id}",
        case_ids=cases,
        waived=waived,
        waiver_owner="o" if waived else None,
        waiver_reason="r" if waived else None,
        waiver_expires_at="2099-01-01T00:00:00Z" if waived else None,
    )


def _decision(*gates, name="s", decision="BLOCK"):
    return ReleaseDecision("1.0", name, decision, decision == "PASS", tuple(gates))


def test_junit_distinguishes_block_warn_and_waived() -> None:
    decision = _decision(
        _gate("global:a:minimum"),
        _gate("global:b:minimum", severity="warn"),
        _gate("global:c:minimum", waived=True),
        _gate("global:d:minimum", passed=True),
    )
    root = ET.fromstring(junit_xml(decision))

    assert root.attrib == {"name": "ragops: s", "tests": "4", "failures": "1", "skipped": "2"}
    cases = {case.attrib["name"]: case for case in root}
    assert cases["global:a:minimum"].find("failure").attrib["type"] == "metrics.global:a:minimum"
    assert cases["global:b:minimum"].find("skipped").attrib["message"].startswith("warning: ")
    assert cases["global:c:minimum"].find("skipped").attrib["message"].startswith("waived: ")
    assert len(cases["global:d:minimum"]) == 0
    assert all(case.attrib["classname"] == "ragops.release_gate" for case in root)
    assert "observed 0.5 must be >= 0.8; cases=q1" in cases["global:a:minimum"].find("failure").text


def test_message_lists_no_cases_as_none() -> None:
    root = ET.fromstring(junit_xml(_decision(_gate("global:a:minimum", cases=()))))
    assert root[0].find("failure").text.endswith("cases=none")


def test_github_summary_exact_and_bounded() -> None:
    decision = _decision(_gate("global:a:minimum"), _gate("global:b:minimum", severity="warn"), _gate("global:c:minimum", passed=True))
    assert github_summary(decision) == (
        "## RAGOps release gate: BLOCK\n\nScenario: `s`\n\n"
        "| Gate | Scope | Observed | Threshold | Result |\n| --- | --- | ---: | ---: | --- |\n"
        "| `global:a:minimum` | `global` | 0.5 | >= 0.8 | BLOCK |\n"
        "| `global:b:minimum` | `global` | 0.5 | >= 0.8 | WARN |\n"
        "| `global:c:minimum` | `global` | 0.5 | >= 0.8 | PASS |\n"
    )
    short = github_summary(decision, max_gates=1)
    assert "global:b:minimum" not in short and short.endswith("\n2 additional gates omitted.\n")
    assert github_summary(decision, max_gates=0).count("| `global:") == 1  # floor of one gate
    assert github_summary(decision, max_gates=1000).count("| `global:") == 3  # ceiling is not exceeded


def test_github_summary_escapes_untrusted_names() -> None:
    decision = _decision(_gate("global:a|b`c\\d:minimum"), name="x|y")
    text = github_summary(decision)
    assert "x\\|y" in text and "a\\|b\\`c\\\\d" in text


def test_sarif_levels_rules_and_results() -> None:
    decision = _decision(
        _gate("global:a:minimum"),
        _gate("global:b:minimum", severity="warn"),
        _gate("global:c:minimum", waived=True),
        _gate("global:d:minimum", passed=True),
    )
    sarif = sarif_report(decision)
    run = sarif["runs"][0]
    driver = run["tool"]["driver"]

    assert sarif["$schema"].endswith("sarif-2.1.0.json") and sarif["version"] == "2.1.0"
    assert driver["name"] == "RAGOps" and driver["informationUri"] == "https://github.com/thangldw/ragops"
    assert [rule["id"] for rule in driver["rules"]] == ["global:a:minimum", "global:b:minimum", "global:c:minimum"]
    assert driver["rules"][0] == {
        "id": "global:a:minimum",
        "name": "global_a_minimum",
        "shortDescription": {"text": "metrics.global:a:minimum"},
        "properties": {"severity": "block", "scope": "global"},
    }
    assert [item["level"] for item in run["results"]] == ["error", "warning", "note"]
    assert run["results"][0]["properties"] == {
        "policyPath": "metrics.global:a:minimum",
        "caseIds": ["q1"],
        "waived": False,
    }
    assert run["results"][2]["properties"]["waived"] is True


def test_sarif_rule_names_are_identifier_safe_and_bounded() -> None:
    sarif = sarif_report(_decision(_gate("g/" + "x" * 200 + ":m")))
    name = sarif["runs"][0]["tool"]["driver"]["rules"][0]["name"]
    assert len(name) == 128 and name.startswith("g_x")
    empty = sarif_report(_decision(_gate("")))
    assert empty["runs"][0]["tool"]["driver"]["rules"][0]["name"] == "ragops_gate"


def test_pr_comment_exact_for_blocking_passing_and_truncated() -> None:
    blocking = _decision(_gate("global:a:minimum", cases=tuple(f"c{i}" for i in range(7))))
    text = pr_comment(blocking, max_cases=5)
    assert text.startswith(COMMENT_MARKER + "\n### RAGOps release gate: **BLOCK**\n\n**What to change**\n\n- ")
    assert "affected: `c0`, `c1`, `c2`, `c3`, `c4` (+2 more)" in text
    assert "raise to at least 0.8 (change by 0.3)" in text
    assert text.rstrip().endswith("</details>")

    lower = pr_comment(_decision(_gate("global:l:maximum", observed=0.9, threshold=0.5, comparator="<=")))
    assert "reduce to at most 0.5 (change by 0.4)" in lower

    many = _decision(*[_gate(f"global:g{i}:minimum") for i in range(4)])
    assert "- … and 2 more failing gates" in pr_comment(many, max_items=2)

    passing = _decision(_gate("global:a:minimum", passed=True), decision="PASS")
    assert "All gates passed." in pr_comment(passing)
    waived_only = _decision(_gate("global:a:minimum", waived=True), decision="WARN")
    assert "All gates passed." not in pr_comment(waived_only) and "What to change" not in pr_comment(waived_only)


def test_render_ci_dispatch_and_unknown_format() -> None:
    decision = _decision(_gate("global:a:minimum"))
    assert render_ci(decision, "junit") == junit_xml(decision)
    assert render_ci(decision, "github") == github_summary(decision)
    assert render_ci(decision, "comment") == pr_comment(decision)
    assert json.loads(render_ci(decision, "sarif")) == sarif_report(decision)
    assert render_ci(decision, "sarif").endswith("}\n")
    with pytest.raises(ValueError, match="Unsupported CI format: nope"):
        render_ci(decision, "nope")


def test_junit_counts_are_exact_and_declaration_present() -> None:
    decision = _decision(
        _gate("global:a:minimum"),
        _gate("global:p1:minimum", passed=True),
        _gate("global:p2:minimum", passed=True),
        _gate("global:w1:minimum", waived=True),
        _gate("global:w2:minimum", waived=True),
    )
    text = junit_xml(decision)
    assert text.startswith("<?xml version='1.0' encoding='utf-8'?>\n<testsuite ")
    assert text.endswith("</testsuite>\n")
    assert ET.fromstring(text).attrib["failures"] == "1"
    assert ET.fromstring(text).attrib["skipped"] == "2"


def test_github_summary_omitted_message_boundaries() -> None:
    three = _decision(*[_gate(f"global:g{i}:minimum") for i in range(3)])
    assert "omitted" not in github_summary(three, max_gates=3)
    assert github_summary(three, max_gates=2).endswith("\n1 additional gates omitted.\n")
    many = _decision(*[_gate(f"global:g{i}:minimum") for i in range(101)])
    text = github_summary(many, max_gates=1000)
    assert text.count("| `global:") == 100 and "1 additional gates omitted." in text
    assert "| WAIVED |" in github_summary(_decision(_gate("global:w:minimum", waived=True)))


def test_pr_comment_affected_case_boundaries_and_exact_text() -> None:
    def one(n):
        return pr_comment(_decision(_gate("global:a:minimum", cases=tuple(f"c{i}" for i in range(n)))), max_cases=2)

    assert "affected: `c0`, `c1` (+1 more)" in one(3)
    assert "affected: `c0`, `c1`;" not in one(2) and "affected: `c0`, `c1` (" not in one(2)
    assert "; affected" not in one(0)
    exactly = pr_comment(_decision(_gate("global:a:minimum"), _gate("global:b:minimum")), max_items=2)
    assert "more failing gates" not in exactly
    assert pr_comment(_decision(_gate("global:a:minimum")), max_items=1).count("more failing gates") == 0

    assert pr_comment(_decision(_gate("global:a:minimum", passed=True), decision="PASS")) == (
        f"{COMMENT_MARKER}\n### RAGOps release gate: **PASS**\n\nAll gates passed.\n\n"
        "<details><summary>All gates</summary>\n\n"
        "Scenario: `s`\n\n"
        "| Gate | Scope | Observed | Threshold | Result |\n| --- | --- | ---: | ---: | --- |\n"
        "| `global:a:minimum` | `global` | 0.5 | >= 0.8 | PASS |\n\n</details>\n"
    )


def test_sarif_render_keeps_unicode_and_indentation() -> None:
    rendered = render_ci(_decision(_gate("global:a:minimum", cases=("日本語",))), "sarif")
    assert "日本語" in rendered and '\n  "version": "2.1.0"' in rendered
