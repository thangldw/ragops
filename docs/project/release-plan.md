# Release plan

## Release readiness

1. Requirement and ADR are linked from the change.
2. Public contracts are versioned and backwards compatibility is tested.
3. Lint and tests pass on supported Python versions.
4. Sample evaluate and compare commands produce expected exit codes.
5. Security-sensitive behavior has negative tests.
6. Documentation and changelog match the shipped behavior.
7. Product owner accepts the demo and limitations.

## Version policy

- Patch: compatible defect or documentation correction.
- Minor: compatible capability or optional contract extension.
- Major: incompatible public API, schema, or release-decision semantics.

The v2.0 API authentication correction is major because protected endpoints
that previously allowed an unset key now fail closed unless explicit insecure
development mode is enabled.

## Rollback

Do not rewrite a published contract. Restore the last working release, publish
a corrective patch, and add the failure as a permanent regression test.
