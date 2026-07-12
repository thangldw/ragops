from __future__ import annotations

import html

from ragops.models import ComparisonReport, EvaluationReport


def evaluation_markdown(report: EvaluationReport) -> str:
    status = "PASS" if report.passed else "FAIL"
    lines = [
        f"# RAGOps evaluation: {status}",
        "",
        f"Scenario: `{report.scenario_id}`",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    lines.extend(f"| {name} | {_format(value)} |" for name, value in report.metrics.items())
    lines.extend(["", "## Failed gates", ""])
    lines.extend(f"- `{gate}`" for gate in report.failed_gates)
    if not report.failed_gates:
        lines.append("None.")
    return "\n".join(lines) + "\n"


def comparison_markdown(report: ComparisonReport) -> str:
    status = "PASS" if report.passed else "FAIL"
    lines = [
        f"# RAGOps regression check: {status}",
        "",
        f"Scenario: `{report.scenario_id}`",
        "",
        "| Metric | Baseline | Candidate | Delta |",
        "| --- | ---: | ---: | ---: |",
    ]
    for name, delta in report.deltas.items():
        lines.append(
            f"| {name} | {_format(report.baseline.metrics[name])} | "
            f"{_format(report.candidate.metrics[name])} | {_signed(delta)} |"
        )
    lines.extend(["", "## Failed gates", ""])
    lines.extend(f"- `{gate}`" for gate in report.failed_gates)
    if not report.failed_gates:
        lines.append("None.")
    return "\n".join(lines) + "\n"


def comparison_html(report: ComparisonReport) -> str:
    status = "PASS" if report.passed else "FAIL"
    status_class = "pass" if report.passed else "fail"
    rows = "".join(
        "<tr>"
        f"<td>{html.escape(name)}</td>"
        f"<td>{_format(report.baseline.metrics[name])}</td>"
        f"<td>{_format(report.candidate.metrics[name])}</td>"
        f"<td>{_signed(delta)}</td>"
        "</tr>"
        for name, delta in report.deltas.items()
    )
    gates = "".join(f"<li><code>{html.escape(gate)}</code></li>" for gate in report.failed_gates)
    gates = gates or "<li>None</li>"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>RAGOps regression report</title>
<style>
body{{font:16px system-ui;max-width:960px;margin:40px auto;padding:0 20px;color:#172033}}
.status{{display:inline-block;padding:6px 12px;border-radius:999px;font-weight:700}}
.pass{{background:#d1fae5;color:#065f46}}.fail{{background:#fee2e2;color:#991b1b}}
table{{border-collapse:collapse;width:100%;margin:24px 0}}th,td{{padding:10px;border-bottom:1px solid #d7dce5;text-align:right}}
th:first-child,td:first-child{{text-align:left}}code{{background:#f3f4f6;padding:2px 5px;border-radius:4px}}
</style></head><body>
<h1>RAGOps regression report</h1><p class="status {status_class}">{status}</p>
<p>Scenario: <code>{html.escape(report.scenario_id)}</code></p>
<table><thead><tr><th>Metric</th><th>Baseline</th><th>Candidate</th><th>Delta</th></tr></thead>
<tbody>{rows}</tbody></table><h2>Failed gates</h2><ul>{gates}</ul>
</body></html>"""


def _format(value: float) -> str:
    return f"{value:.4f}".rstrip("0").rstrip(".")


def _signed(value: float) -> str:
    return f"{value:+.4f}".rstrip("0").rstrip(".")
