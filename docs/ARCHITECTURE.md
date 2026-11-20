# RAGOps architecture

```mermaid
%%{init: {"theme":"base","themeVariables":{"background":"#FFFFFF","fontFamily":"Arial, sans-serif","lineColor":"#667085","primaryTextColor":"#172B4D"}}}%%
flowchart LR
    T["Portable traces"]:::yellow
    S["Scenario & policy"]:::blue
    C["Dependency-free core"]:::purple
    E["Evidence bundle"]:::pink
    G{"PASS / WARN / BLOCK"}:::green
    T --> C
    S --> C --> E --> G
    classDef yellow fill:#FFF4A3,stroke:#C9A227,stroke-width:2px,color:#172B4D
    classDef blue fill:#D9EAFD,stroke:#4C78A8,stroke-width:2px,color:#172B4D
    classDef purple fill:#E9DDF7,stroke:#8064A2,stroke-width:2px,color:#172B4D
    classDef pink fill:#FFE1E6,stroke:#C96A7B,stroke-width:2px,color:#172B4D
    classDef green fill:#DDF5E3,stroke:#4F9D69,stroke-width:2px,color:#172B4D
```

`src/ragops/` owns portable contracts, deterministic evaluators, slice/distribution analysis, policy decisions, calibration, evidence bundles, adapters, and SQLite governance. `src/ragops/api/` and `src/ragops/web/` are optional packaged adapters; importing the core never imports FastAPI, Uvicorn, or vendor SDKs. `apps/api/main.py` is a source compatibility shim. CLI/API/UI and CI renderers consume the same canonical decision evidence.

The production-loop modules sit beside the gate and reuse the same contracts: `policy_suggest.py` drafts a policy from a baseline, `calibration.py` and `triage.py` decide where the scorer can be trusted, `stability.py` compares repeated runs of a replay bundle, `mine.py` turns flagged production logs into scenario cases, and `counterfactual.py` alters evidence and re-asks a user-supplied command (with a self-test of its own checks). Each is an offline command that reads and writes JSON/TOML files; none imports a network client. See [production-loop.md](production-loop.md) and [counterfactual-test.md](counterfactual-test.md).
