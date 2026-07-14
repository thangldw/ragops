# Component architecture

```mermaid
%%{init: {"theme":"base","fontFamily":"system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif","flowchart":{"curve":"basis"},"themeVariables":{"background":"#f8f6f0","primaryColor":"#ffdc7c","primaryTextColor":"#17152f","primaryBorderColor":"#17152f","secondaryColor":"#bfe8ff","tertiaryColor":"#d8ceff","lineColor":"#756f84","edgeLabelBackground":"#fffef9"}}}%%
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
    classDef adapter fill:#bfe8ff,stroke:#17152f,color:#17152f,stroke-width:2px;
    classDef core fill:#ffdc7c,stroke:#17152f,color:#17152f,stroke-width:2px;
    classDef output fill:#aee8c9,stroke:#17152f,color:#17152f,stroke-width:2px;
    classDef contract fill:#d8ceff,stroke:#17152f,color:#17152f,stroke-width:2px;
    class CLI,API,Web adapter;
    class Loader,Engine,Builtin,Plugins core;
    class Reports,Renderers,Store output;
    class Schemas contract;
```

## Dependency rule

Dependencies point inward toward models and engine semantics. Adapters may
depend on the core; the core must not depend on FastAPI, browser assets,
provider SDKs, or hosted infrastructure.
