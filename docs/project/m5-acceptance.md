# M5 acceptance — commercial control-plane alpha

## Decision

**Accepted as a local architecture alpha, not a hosted production service.** It
proves the open-core/hosted boundary and workspace workflow without claiming
enterprise security certification.

## Evidence

- Workspace creation with generated high-entropy API key.
- Digested key storage, constant-time authentication, and rotation.
- Workspace-slug validation and isolated experiment-store paths.
- Audit events for workspace lifecycle and store access.
- CLI management commands and API workspace-store selection.
- Persisted workspace evaluation endpoint.
- Isolation, rotation, invalid-auth, and traversal tests.

## External validation required before hosted launch

- Legal entity, terms, privacy policy, and data-processing agreements.
- Cloud account, domain, managed identity/database, secrets, backups, alerts,
  billing, support, and incident response.
- Threat modeling and penetration test against the deployed environment.
- Design-partner evidence and willingness-to-pay validation.

