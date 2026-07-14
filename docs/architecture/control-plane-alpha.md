# Control-plane alpha architecture

```mermaid
%%{init: {"theme":"base","fontFamily":"system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif","flowchart":{"curve":"basis"},"themeVariables":{"background":"#f8f6f0","primaryColor":"#ffdc7c","primaryTextColor":"#17152f","primaryBorderColor":"#17152f","secondaryColor":"#bfe8ff","tertiaryColor":"#d8ceff","lineColor":"#756f84","edgeLabelBackground":"#fffef9"}}}%%
flowchart LR
    Client["Workspace client"] -->|workspace id + key| API["RAGOps API"]
    API --> Auth["Hashed-key authentication"]
    Auth --> Index["Workspace index + audit events"]
    Auth --> StoreA["Workspace A runs.db"]
    Auth --> StoreB["Workspace B runs.db"]
    classDef client fill:#bfe8ff,stroke:#17152f,color:#17152f,stroke-width:2px;
    classDef control fill:#ffdc7c,stroke:#17152f,color:#17152f,stroke-width:2px;
    classDef store fill:#d8ceff,stroke:#17152f,color:#17152f,stroke-width:2px;
    class Client client;
    class API,Auth control;
    class Index,StoreA,StoreB store;
```

## Implemented alpha controls

- Validated workspace slugs prevent path traversal.
- Random high-entropy keys are stored only as SHA-256 digests.
- Constant-time digest comparison and key rotation.
- Separate experiment database path for each workspace.
- Workspace creation, key rotation, store access, and audit events.
- API workspace headers select the authenticated store.

## Not production-ready

- SHA-256 is suitable here only because generated API keys have high entropy;
  human passwords require a password KDF.
- SQLite files do not provide production tenant isolation, HA, backups, or
  concurrent SaaS operations.
- Audit events are mutable by filesystem/database administrators.
- There is no SSO, RBAC, envelope encryption, rate limiting, billing, regional
  residency, queue, or incident-response integration.

Production commercialization requires a managed database with row-level tenant
policies, external identity, secrets management, immutable audit export, and an
independent security review.
