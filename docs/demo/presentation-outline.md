# Ten-minute presentation outline

**Audience:** engineering, platform, or product leaders responsible for RAG or
AI-agent releases.

**Decision:** whether to pilot RAGOps as a release gate around an existing
system.

## 1. Release question — 60 seconds

Show how a candidate can remain fluent while citations, evidence support,
latency, cost, or safety regress. Ask: “Is this change still good enough to
release?”

## 2. Product thesis — 60 seconds

Position RAGOps as a provider-independent policy and evidence layer, not an
orchestration framework, model host, or observability replacement.

## 3. Workflow — 90 seconds

Walk through record → evaluate → compare → gate. Use the board-style workflow
visual so every transition names its input and output.

## 4. Live evidence — 180 seconds

Run `ragops demo`, open the HTML report, and trace one aggregate regression to
its case, citations, metric delta, and versioned policy rule. Demonstrate both
the passing baseline and blocked candidate.

## 5. Architecture — 90 seconds

Map responses, traces, and optional external scores into the dependency-free
core. Keep providers, API, browser, and collaboration surfaces outside it.

## 6. Limitations and rollout — 90 seconds

Separate synthetic evidence from production claims. Recommend one reviewed
workflow fixture, one owner, and a human-approved release decision before
expanding coverage.

## 7. Close — 30 seconds

“Evaluate with evidence. Release with a reason.”

Keep static fallbacks available: the two SVG infographics, benchmark report,
and generated standalone HTML report.
