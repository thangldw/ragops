# Threat model

## Assets

- Evaluation datasets and trusted evidence.
- Recorded application outputs and potentially sensitive traces.
- Release policies, accepted baselines, and decision history.
- API credentials and future provider credentials.

## Trust boundaries

- Application to trace importer.
- Local files to contract loader.
- Browser/API client to FastAPI adapter.
- Core to optional evaluator plugins or providers.
- Open-source client to future hosted control plane.

## Priority threats

1. Malformed or oversized input causing denial of service.
2. Sensitive trace data written to reports or logs without review.
3. Malicious plugin executing with process privileges.
4. Baseline tampering causing regressions to appear acceptable.
5. Unauthorized API evaluation or access to stored reports.
6. Prompt injection influencing provider-backed evaluators.
7. Cross-project or cross-tenant data exposure in a hosted service.

## Current controls and limitations

- Strict loader checks, versioned contracts, offline core, optional API key,
  non-root container, and read-only compose defaults reduce baseline risk.
- Plugin sandboxing, signed baselines, payload limits, production identity,
  encryption, tenant isolation, and provider data controls are not implemented.
- Do not process customer-sensitive traces until the deployment owner completes
  a data-classification and retention review.

