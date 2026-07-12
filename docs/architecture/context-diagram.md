# System context

```mermaid
flowchart LR
    Engineer["AI engineer / FDE"] -->|authors| Scenario["Versioned scenario"]
    Application["RAG or agent application"] -->|exports| Trace["Portable traces"]
    Scenario --> Core["RAGOps local core"]
    Trace --> Core
    Core --> Report["Evidence and release decision"]
    Report --> CI["CI / pull request"]
    Report --> Reviewer["Engineering and governance review"]
    Core -. optional .-> Plugin["Evaluator plugins / model judges"]
    Core -. optional .-> Hosted["Future team control plane"]
```

RAGOps is never the system of record for enterprise knowledge and does not
execute business actions. It evaluates artifacts produced by another system.

