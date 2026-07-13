# CV and LinkedIn copy

Use after owner review; these statements describe public repository evidence,
not customer production adoption.

## CV project entry

**RAGOps — Open-source evaluation and release infrastructure for RAG/agents**

- Designed and shipped a dependency-free Python evaluation core with versioned
  scenarios/traces, regression gates, red-team policies, CLI/API, CI, Docker,
  experiment review/trends, and a workspace control-plane alpha.
- Built a 30-case synthetic Japanese-question release-gate fixture and ACL-first
  graph-assisted troubleshooting reference agent; RAGOps blocked a lexical-only
  candidate with 25-point citation coverage/precision regressions. The fixture
  validates harness behavior, not Japanese semantic quality.
- Published architecture decisions, threat model, rollout plan, executive
  go/no-go recommendation, reproducible reports, and a v2.4.0 release validated
  by 144 automated tests.

## LinkedIn project description

RAGOps is the provider-independent evidence layer between an AI change and a
release decision. It evaluates recorded RAG/agent output, applies versioned
quality and operational policy, and produces an explainable PASS or BLOCK report
locally. The public synthetic fixture validates the harness—not customer
adoption, production security, or Japanese semantic quality.

Repository: https://github.com/thangldw/ragops
Case study: https://thangldw.github.io/projects/ragops/
