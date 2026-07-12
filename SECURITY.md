# Security policy

## Supported versions

The latest minor version receives security fixes. Before public launch,
security reports should be sent privately to the repository owner rather than
opened as public issues.

## Data handling

RAGOps core runs offline and does not transmit scenarios, responses, or traces.
Provider-backed plugins are responsible for clearly documenting transmission
and retention. Never put production secrets or personal data in public fixtures.

## Deployment guidance

- Set `RAGOPS_API_KEY` when the API is reachable outside localhost.
- Terminate TLS at a trusted reverse proxy.
- Run the provided image as its non-root user and keep the filesystem read-only.
- Put experiment databases on an encrypted, access-controlled volume.
- Treat reports as sensitive because answers and evidence may be embedded.
- Apply request-size and rate limits at the ingress for internet-facing use.

## Known v1.0 limitations

- API-key authentication is single-tenant and is not an identity system.
- Lexical groundedness is a transparent baseline, not semantic verification.
- The bundled dashboard is an operator workbench, not a hardened multi-user UI.

