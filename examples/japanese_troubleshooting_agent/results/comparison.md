# RAGOps regression check: FAIL

Scenario: `jp-reference-agent-v1`

| Metric | Baseline | Candidate | Delta |
| --- | ---: | ---: | ---: |
| citation_coverage | 1 | 0.75 | -0.25 |
| citation_precision | 1 | 0.75 | -0.25 |
| lexical_groundedness | 1 | 0.7812 | -0.2188 |
| avg_latency_ms | 1 | 1 | +0 |
| avg_cost_usd | 0 | 0 | +0 |
| critical_findings | 0 | 0 | +0 |

## Failed gates

- `candidate_release_gate`
- `citation_coverage_regression`
- `citation_precision_regression`
- `groundedness_regression`
