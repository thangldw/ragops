# Security model

## Trust boundaries

- The evaluated RAG or agent application is outside RAGOps.
- Scenarios, responses, traces, reports, and CI artifacts may contain sensitive
  content and must be treated as data, never executable input.
- Provider adapters may transmit data; the offline core does not.
- Pull-request code and artifacts are untrusted across any write-enabled
  publisher boundary.

## Required controls

- Validate every public contract and reject unknown, invalid, non-finite, or
  oversized input.
- Configure `RAGOPS_API_KEY` for protected API endpoints. Use
  `RAGOPS_INSECURE_DEV_MODE=true` only for explicit local development.
- Bind the sample API to localhost, terminate TLS at a trusted proxy, apply
  ingress rate limits, and store reports/databases on protected volumes.
- Redact secrets, personal data, private prompts, and unnecessary evidence
  before export.
- Run containers as non-root with read-only filesystems where practical.
- Keep PR evaluation read-only and isolate comment publication from untrusted
  code, caches, templates, and shell interpolation.

## Local control-plane boundary

The alpha uses workspace-specific SQLite paths, generated API-key digests,
constant-time comparison, rotation, and audit events. It is not a production
tenant boundary: there is no SSO/RBAC, managed secrets, immutable audit export,
regional residency, HA, backup policy, billing, or independent penetration
test.

## Evidence limits

The bundled attack suite and deterministic detectors establish repeatable
coverage only. Zero findings do not prove security. Production use requires a
deployment-specific threat model, independent review, operational controls, and
human approval for consequential actions.
