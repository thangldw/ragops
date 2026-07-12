# Reference architecture

```mermaid
flowchart LR
    User["Field engineer"] --> Agent["Workflow agent"]
    Agent --> ACL["Role ACL filter"]
    ACL --> Lexical["Lexical retrieval"]
    ACL --> Graph["Entity graph expansion"]
    Lexical --> Rank["Authority + intent ranker"]
    Graph --> Rank
    Rank --> Decision["Answer / clarify / escalate / approval"]
    Decision --> Trace["Portable trace 0.4"]
    Trace --> RAGOps["RAGOps release gate"]
```

The reference application owns retrieval and workflow behavior. RAGOps owns
evaluation contracts, evidence, comparison, and the release decision.

## Production substitutions

- Synthetic JSON documents -> governed enterprise connectors.
- Role lists -> SSO claims plus source-system ACL enforcement.
- Explicit graph -> versioned extraction pipeline and graph store.
- Deterministic composer -> provider adapter with structured output.
- Local JSONL -> OpenTelemetry/export queue with redaction and retention.

