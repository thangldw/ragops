# System architecture

```mermaid
%%{init: {"theme":"base","fontFamily":"system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif","flowchart":{"curve":"basis"},"themeVariables":{"background":"#f8f6f0","primaryColor":"#ffdc7c","primaryTextColor":"#17152f","primaryBorderColor":"#17152f","secondaryColor":"#bfe8ff","tertiaryColor":"#d8ceff","lineColor":"#756f84","edgeLabelBackground":"#fffef9","clusterBkg":"#fffef9","clusterBorder":"#b9b4aa"}}}%%
flowchart LR
    APP["RAG / AI agent<br/>existing application"]
    TRACE["Portable evidence<br/>responses · traces · metrics"]
    SCENARIO["Versioned contract<br/>scenario · policy"]

    subgraph CORE["DEPENDENCY-FREE CORE"]
        LOAD["Load + validate"]
        EVAL["Evaluate<br/>metrics + findings"]
        COMPARE["Compare<br/>baseline + candidate"]
        REPORT["Report<br/>JSON · Markdown · HTML"]
        LOAD --> EVAL --> COMPARE --> REPORT
    end

    GATE{"Release gate"}
    PASS["PASS"]
    BLOCK["BLOCK"]
    REVIEW["Engineer · CI · review"]
    ADAPTERS["Optional adapters<br/>API · browser · providers · publishers"]

    APP --> TRACE --> LOAD
    SCENARIO --> LOAD
    REPORT --> GATE
    GATE --> PASS
    GATE --> BLOCK
    REPORT --> REVIEW
    ADAPTERS -.-> LOAD

    classDef input fill:#bfe8ff,stroke:#17152f,color:#17152f,stroke-width:2px;
    classDef core fill:#ffdc7c,stroke:#17152f,color:#17152f,stroke-width:2px;
    classDef evidence fill:#d8ceff,stroke:#17152f,color:#17152f,stroke-width:2px;
    classDef pass fill:#aee8c9,stroke:#17152f,color:#17152f,stroke-width:2px;
    classDef block fill:#ffc0dd,stroke:#17152f,color:#8d2037,stroke-width:2px;
    class APP,TRACE,SCENARIO input;
    class LOAD,EVAL,COMPARE core;
    class REPORT,GATE,REVIEW,ADAPTERS evidence;
    class PASS pass;
    class BLOCK block;
```

## Dependency rule

`src/ragops/` owns models, loaders, evaluation, comparison, findings, and
reports using only the Python standard library. `apps/`, providers, examples,
and workflows may depend on the core; the core never depends on them.

## Data model

- A **scenario** defines cases, expected evidence, thresholds, and policy.
- A **response** or **trace** records observed application behavior.
- A **replay bundle** records per-case, per-repeat metrics and complete
  comparison provenance.
- An **evaluation** contains per-case evidence, aggregate metrics, findings, and
  an absolute decision.
- A **comparison** evaluates baseline and candidate under the same contract,
  calculates deltas, and applies regression tolerances.
- A **report** serializes the evidence and named gate reasons.
- An **accepted baseline manifest** binds exact bundle and policy bytes; an
  optional signing adapter establishes owner identity.

Public schemas are versioned. SQLite history and review metadata are local
operational state, not part of the portable evaluation contract.

## Boundaries

- RAGOps never becomes the knowledge source or action executor.
- Optional provider metrics enter through stable adapters with explicit
  provenance and meaning.
- The required path stays offline and makes a complete release decision without
  a hosted service.
- Consequential actions remain subject to human approval.
