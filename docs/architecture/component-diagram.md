# Component architecture

```mermaid
flowchart TB
    CLI["CLI"] --> Loader
    API["FastAPI adapter"] --> Loader
    Web["Browser workbench"] --> API
    Loader["Contract loaders"] --> Engine["Evaluation engine"]
    Engine --> Builtin["Deterministic evaluators"]
    Engine --> Plugins["Case evaluator plugins"]
    Engine --> Reports["Evaluation / comparison reports"]
    Reports --> Renderers["JSON / Markdown / HTML"]
    Reports --> Store["Local SQLite history"]
    Schemas["Published JSON Schemas"] -. validates .-> Loader
```

## Dependency rule

Dependencies point inward toward models and engine semantics. Adapters may
depend on the core; the core must not depend on FastAPI, browser assets,
provider SDKs, or hosted infrastructure.

