# Portfolio case study copy

## RAGOps — release confidence for RAG and agent systems

AI pilots often fail at the transition to production because quality evidence,
security checks, operational budgets, and release decisions live in separate
tools. I designed RAGOps as a local-first evaluation and red-team harness that
turns these expectations into one versioned release contract.

The open-source core evaluates portable application traces, applies absolute
and baseline regression gates, and exports explainable JSON, Markdown, and HTML
reports. A Japanese enterprise troubleshooting scenario demonstrates how an
FDE can translate ambiguous customer expectations into cases, policies, and a
go/no-go recommendation.

### What this demonstrates

- Product framing and open-core strategy.
- Stable contracts, CLI/API adapters, and dependency-free Python design.
- Evaluation, red-team, cost, latency, and regression thinking.
- CI, testing, container security, and explicit architecture trade-offs.

### Honest current boundary

RAGOps evaluates recorded responses; it is not an orchestration framework. The
next milestone adds a larger benchmark and reference RAG/agent deployment while
keeping that boundary intact.

