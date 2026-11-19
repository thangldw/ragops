"""Self-contained interactive comparison report.

One HTML file, no network, no external assets. Filters toggle ``hidden`` on
pre-rendered cards, so no untrusted text is ever written with ``innerHTML``; a
Content-Security-Policy allows only the single inline script (by SHA-256) and
inline styles.
"""

from __future__ import annotations

import base64
import hashlib
import html
from collections.abc import Sequence

from ragops.evaluators import unsupported_spans
from ragops.models import CaseResult, ComparisonReport, RecordedResponse, Scenario

SCRIPT = """
(function () {
  var cards = Array.prototype.slice.call(document.querySelectorAll('.case'));
  var controls = {
    category: document.getElementById('f-category'),
    language: document.getElementById('f-language'),
    severity: document.getElementById('f-severity'),
    status: document.getElementById('f-status'),
    text: document.getElementById('f-text')
  };
  var counter = document.getElementById('count');
  function apply() {
    var shown = 0;
    var needle = controls.text.value.trim().toLowerCase();
    cards.forEach(function (card) {
      var ok = ['category', 'language', 'severity', 'status'].every(function (key) {
        return controls[key].value === '' || card.dataset[key] === controls[key].value;
      }) && (needle === '' || card.dataset.search.indexOf(needle) !== -1);
      card.hidden = !ok;
      if (ok) { shown += 1; }
    });
    counter.textContent = shown + ' of ' + cards.length + ' cases';
  }
  Object.keys(controls).forEach(function (key) {
    controls[key].addEventListener(key === 'text' ? 'input' : 'change', apply);
  });
  document.getElementById('expand').addEventListener('click', function () {
    var open = cards.some(function (card) { return !card.hidden && !card.open; });
    cards.forEach(function (card) { if (!card.hidden) { card.open = open; } });
  });
  var worst = document.getElementById('f-status');
  if (cards.some(function (card) { return card.dataset.status === 'regressed'; })) {
    worst.value = 'regressed';
  }
  apply();
})();
"""

STYLE = """
:root{color-scheme:light dark;--bg:#fff;--fg:#172033;--muted:#5f6b7a;--line:#d7dce5;--bad:#991b1b;--badbg:#fee2e2;--good:#065f46;--goodbg:#d1fae5;--mark:#fde68a}
@media (prefers-color-scheme:dark){:root{--bg:#0f1520;--fg:#e6ebf2;--muted:#9aa7b8;--line:#2b3547;--bad:#fecaca;--badbg:#5b1f1f;--good:#a7f3d0;--goodbg:#12392c;--mark:#6b5a12}}
body{font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif;background:var(--bg);color:var(--fg);max-width:1100px;margin:32px auto;padding:0 16px}
h1{margin:0 0 4px}.pill{display:inline-block;padding:4px 12px;border-radius:999px;font-weight:700}
.pass{background:var(--goodbg);color:var(--good)}.fail{background:var(--badbg);color:var(--bad)}
table{border-collapse:collapse;width:100%;margin:12px 0}th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:right}th:first-child,td:first-child{text-align:left}
code{background:rgba(127,127,127,.15);padding:1px 5px;border-radius:4px}
.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:16px 0;position:sticky;top:0;background:var(--bg);padding:8px 0;z-index:1}
.bar select,.bar input,.bar button{font:inherit;padding:4px 8px;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px}
.case{border:1px solid var(--line);border-radius:8px;margin:8px 0;padding:0 12px}.case[hidden]{display:none}
.case>summary{cursor:pointer;padding:10px 0;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.tag{font-size:12px;padding:1px 8px;border-radius:999px;border:1px solid var(--line);color:var(--muted)}
.tag.regressed{color:var(--bad);border-color:var(--bad)}.tag.changed{color:var(--fg)}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:12px}@media (max-width:700px){.cols{grid-template-columns:1fr}}
.col{border:1px solid var(--line);border-radius:6px;padding:8px 10px}.col h4{margin:0 0 6px;color:var(--muted);font-size:13px}
mark{background:var(--mark);color:inherit;border-radius:2px;padding:0 1px}
.evidence{color:var(--muted);font-size:13px}.finding{color:var(--bad)}
.legend{color:var(--muted);font-size:13px}
"""

METRICS = (
    ("citation_coverage", "Citation coverage"),
    ("citation_precision", "Citation precision"),
    ("lexical_groundedness", "Groundedness"),
    ("latency_ms", "Latency ms"),
    ("cost_usd", "Cost USD"),
)


def explorer_html(
    scenario: Scenario,
    baseline: Sequence[RecordedResponse],
    candidate: Sequence[RecordedResponse],
    report: ComparisonReport,
) -> str:
    base_answers = {item.case_id: item for item in baseline}
    cand_answers = {item.case_id: item for item in candidate}
    base_results = {item.case_id: item for item in report.baseline.cases}
    cards = []
    for case in scenario.cases:
        after = next((item for item in report.candidate.cases if item.case_id == case.id), None)
        if after is None:
            continue
        cards.append(
            _card(
                case,
                base_answers.get(case.id),
                cand_answers.get(case.id),
                base_results.get(case.id),
                after,
            )
        )
    status = "PASS" if report.passed else "BLOCK"
    script_hash = base64.b64encode(hashlib.sha256(SCRIPT.encode("utf-8")).digest()).decode("ascii")
    csp = (
        "default-src 'none'; style-src 'unsafe-inline'; "
        f"script-src 'sha256-{script_hash}'; base-uri 'none'; form-action 'none'"
    )
    metric_rows = "".join(
        f"<tr><td>{html.escape(name)}</td><td>{report.baseline.metrics[name]:.4g}</td>"
        f"<td>{report.candidate.metrics[name]:.4g}</td><td>{delta:+.4g}</td></tr>"
        for name, delta in report.deltas.items()
    )
    gates = "".join(f"<li><code>{html.escape(gate)}</code></li>" for gate in report.failed_gates) or "<li>None</li>"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<title>RAGOps report explorer</title><style>{STYLE}</style></head><body>
<h1>RAGOps report explorer</h1>
<p><span class="pill {'pass' if report.passed else 'fail'}">{status}</span>
 Scenario <code>{html.escape(report.scenario_id)}</code></p>
<table><thead><tr><th>Metric</th><th>Baseline</th><th>Candidate</th><th>Delta</th></tr></thead><tbody>{metric_rows}</tbody></table>
<h2>Failed gates</h2><ul>{gates}</ul>
<h2>Cases</h2>
<div class="bar">
{_select('f-category', 'Category', sorted({c.category for c in scenario.cases}))}
{_select('f-language', 'Language', sorted({c.language for c in scenario.cases}))}
{_select('f-severity', 'Severity', sorted({c.severity for c in scenario.cases}))}
{_select('f-status', 'Status', ['regressed', 'changed', 'same'])}
<input id="f-text" type="search" placeholder="Search question or answer" aria-label="Search">
<button id="expand" type="button">Expand / collapse</button><span id="count" role="status"></span>
</div>
<p class="legend">Highlighted words in an answer have no counterpart in the case evidence (lexical check; a visual aid, not a verdict).</p>
{''.join(cards)}
<script>{SCRIPT}</script></body></html>"""


def _select(identifier: str, label: str, values: list[str]) -> str:
    options = "".join(f'<option value="{html.escape(v, quote=True)}">{html.escape(v)}</option>' for v in values)
    return (
        f'<label>{label} <select id="{identifier}"><option value="">All</option>{options}</select></label>'
    )


def _status(before: CaseResult | None, after: CaseResult, changed: bool) -> str:
    if before is not None:
        worse = (
            after.citation_coverage < before.citation_coverage - 1e-9
            or after.citation_precision < before.citation_precision - 1e-9
            or after.lexical_groundedness < before.lexical_groundedness - 1e-9
            or len(after.findings) > len(before.findings)
        )
        if worse:
            return "regressed"
    return "changed" if changed else "same"


def _card(case, before_answer, after_answer, before: CaseResult | None, after: CaseResult) -> str:
    changed = (before_answer.answer if before_answer else None) != (after_answer.answer if after_answer else None)
    status = _status(before, after, changed)
    search = " ".join(
        part for part in (case.question, before_answer.answer if before_answer else "", after_answer.answer if after_answer else "") if part
    ).lower()
    rows = ""
    for key, label in METRICS:
        old = getattr(before, key) if before is not None else None
        new = getattr(after, key)
        rows += (
            f"<tr><td>{label}</td><td>{'' if old is None else f'{old:.4g}'}</td>"
            f"<td>{new:.4g}</td></tr>"
        )
    findings = "".join(
        f'<li class="finding"><code>{html.escape(f.rule)}</code> ({html.escape(f.severity)}): {html.escape(f.message)}</li>'
        for f in after.findings
    ) or "<li>None</li>"
    evidence = "".join(f"<li>{html.escape(item)}</li>" for item in case.evidence)
    return f"""<details class="case" data-category="{html.escape(case.category, quote=True)}" data-language="{html.escape(case.language, quote=True)}" data-severity="{html.escape(case.severity, quote=True)}" data-status="{status}" data-search="{html.escape(search, quote=True)}">
<summary><strong>{html.escape(case.id)}</strong><span class="tag {status}">{status}</span><span class="tag">{html.escape(case.category)}</span><span class="tag">{html.escape(case.language)}</span><span class="tag">{html.escape(case.severity)}</span></summary>
<p>{html.escape(case.question)}</p>
<div class="cols">
<div class="col"><h4>Baseline answer</h4>{_answer(before_answer, case.evidence)}</div>
<div class="col"><h4>Candidate answer</h4>{_answer(after_answer, case.evidence)}</div>
</div>
<table><thead><tr><th>Metric</th><th>Baseline</th><th>Candidate</th></tr></thead><tbody>{rows}</tbody></table>
<p><strong>Candidate findings</strong></p><ul>{findings}</ul>
<p class="evidence"><strong>Evidence</strong></p><ul class="evidence">{evidence}</ul>
</details>"""


def _answer(response: RecordedResponse | None, evidence: tuple[str, ...]) -> str:
    if response is None:
        return "<p><em>No answer recorded.</em></p>"
    text, cursor, parts = response.answer, 0, []
    for start, end in unsupported_spans(text, evidence):
        parts.append(html.escape(text[cursor:start]))
        parts.append(f"<mark>{html.escape(text[start:end])}</mark>")
        cursor = end
    parts.append(html.escape(text[cursor:]))
    citations = ", ".join(f"<code>{html.escape(c)}</code>" for c in response.citation_ids) or "none"
    return f"<p>{''.join(parts)}</p><p class=\"evidence\">Citations: {citations}</p>"
