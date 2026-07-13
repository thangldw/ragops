# ADR 0017: Fail-closed API authentication and bounded input

- Status: Accepted for implementation
- Date: 2026-07-13
- Owner authorization: staged implementation and release requested by Thang on
  2026-07-13; security scan and penetration testing explicitly deferred

## Context

Protected API endpoints currently allow requests when `RAGOPS_API_KEY` is
unset. The sample Compose configuration publishes port 8000 and defaults the
key to an empty value. Request bodies and case counts are not explicitly
bounded, so the sample configuration is unsafe to treat as a deployment
baseline.

## Decision

Protected endpoints fail closed unless a non-empty API key is configured.
Unauthenticated local use requires the explicit
`RAGOPS_INSECURE_DEV_MODE=true` setting and is rejected when combined with an
API key. Health and the static dashboard remain public.

The API adapter enforces configurable request-byte and collection-count limits
before evaluation. The dependency-free core continues to own numeric and
contract validation. Docker Compose binds the API to `127.0.0.1` by default and
does not silently enable insecure mode.

## Compatibility impact

CLI and Python API behavior are unchanged. API deployments that relied on an
unset key must configure a key or explicitly opt into insecure development
mode. This is an intentional fail-closed security correction documented in the
changelog and migration notes.

## Consequences

- Copying the sample deployment no longer exposes protected endpoints on all
  interfaces without an explicit authentication decision.
- The limits reduce accidental resource exhaustion but are not a substitute for
  reverse-proxy rate limiting, tenant quotas, WAF controls, or a security test.
