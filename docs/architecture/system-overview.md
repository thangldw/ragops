# System overview

```text
Scenario JSON ─┐
               ├─> loader ─> evaluation runner ─> report ─> release gate
Responses JSON ┘                    │
                                    ├─ quality evaluators
                                    ├─ operational budget evaluators
                                    └─ red-team policy evaluators
```

The core is a dependency-free Python library. CLI and FastAPI are adapters;
they contain no evaluation logic. Scenario and report formats are explicitly
versioned to allow future migrations.

## Boundary decisions

- RAGOps evaluates a system; it does not own the system's retrieval or LLM.
- The core consumes recorded responses or portable traces so evaluation remains
  reproducible and offline.
- Deterministic lexical groundedness is a transparent baseline, not a claim of
  semantic correctness. Provider-backed judge scores can enter through optional
  adapters and the external metric envelope.
- Critical policy findings always override aggregate averages.
