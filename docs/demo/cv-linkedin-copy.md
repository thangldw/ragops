# CV and LinkedIn copy

Use only after owner review. These statements describe public repository
evidence, not customer production adoption.

## CV project entry

**RAGOps — regression release gates for RAG and AI agents**

- Designed a dependency-free Python evaluation core with versioned scenarios,
  traces, regression policy, red-team checks, CLI/API adapters, CI, Docker, and
  reviewable JSON, Markdown, and HTML evidence.
- Built a thirty-case synthetic Japanese-question benchmark and ACL-first,
  graph-assisted troubleshooting reference agent; the gate blocked a
  lexical-only candidate with 25-point citation coverage and precision
  regressions.
- Published architecture decisions, threat model, rollout guidance, portable
  evaluator integrations, and build-once release verification with checksums
  and SBOM evidence.

## LinkedIn project description

RAGOps is an open-source regression release gate for teams that already have a
RAG or AI agent. It compares recorded candidate behavior with an accepted
baseline, applies versioned quality and operational policy, and produces an
explainable `PASS` or `BLOCK` locally.

The public synthetic fixtures validate the harness and recorded architecture
comparison. They do not prove semantic correctness, production security,
customer adoption, or ROI.

Repository: <https://github.com/thangldw/ragops>

Showcase: <https://thangldw.github.io/ragops/>
