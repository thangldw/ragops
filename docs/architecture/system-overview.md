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
- v0.1 consumes recorded responses so evaluation is reproducible and offline.
- Deterministic lexical groundedness is a transparent baseline, not a claim of
  semantic correctness. Provider-backed semantic judges will be pluggable.
- Critical policy findings always override aggregate averages.

