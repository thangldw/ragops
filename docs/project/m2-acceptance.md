# M2 acceptance — reference deployment

## Decision

**Accepted as a reproducible reference deployment.** It is ready for portfolio
demonstration and customer-reviewed offline extension, not production use.

## Evidence

- Japanese troubleshooting reference agent with graph-assisted retrieval.
- ACL filtering before ranking and approval-aware workflow decisions.
- Portable trace 0.4 with application/build/retriever/generator metadata.
- CLI JSONL trace input for evaluation and comparison.
- Dependency-free generic HTTP JSON adapter.
- Graph versus lexical-only recorded experiment and release decision.
- Discovery, architecture, rollout, limitations, and executive recommendation.
- Automated end-to-end, ACL, action approval, trace, and adapter tests.

## Deferred

- Provider-backed structured generation and graph extraction.
- Production SSO/ACL, queues, retries, rate limiting, and tracing backend.
- Customer-reviewed corpus and measured workflow impact.

