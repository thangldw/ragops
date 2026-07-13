# ADR 0020: Verify local release integrity before publication

Status: Accepted for owner review

## Decision

The quota-independent release lane must install its newly built wheel in a fresh
virtual environment before publication. SHA-256 verification is implemented in
dependency-free Python rather than delegating to platform-specific `shasum` or
`sha256sum` commands. The installed CLI exposes its package version.

## Consequences

Local releases catch missing-package and metadata errors before tags are pushed,
and PyPI promotion works consistently on macOS, Linux, and Windows. Verification
takes slightly longer because it creates an isolated environment. This does not
replace the supported-Python matrix when GitHub Actions capacity returns.
