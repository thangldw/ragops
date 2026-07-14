# Security policy

## Supported version

The latest minor version receives security fixes. Send vulnerability reports
privately to the repository owner through the contact method on their GitHub
profile; do not open a public issue.

Include the affected version, minimal reproduction, impact, and any suggested
mitigation. Do not include real secrets or customer data.

## Deployment baseline

- Configure `RAGOPS_API_KEY` for protected endpoints.
- Keep explicit insecure mode local only.
- Terminate TLS at a trusted proxy and apply ingress request/rate limits.
- Run the container as non-root with a read-only filesystem where practical.
- Protect databases and reports; they may contain answers and evidence.
- Redact sensitive content before provider or telemetry export.

## Known limits

The API key is not enterprise identity. The local control plane is not a
production tenant boundary. The repository has no SSO/RBAC, immutable audit
service, regional residency, HA, managed backup, or independent penetration
test. Lexical groundedness is not semantic verification.

See the full [security model](docs/architecture/security.md).
