# PyPI Trusted Publishing runbook

RAGOps includes a manual, fail-closed publishing workflow at
`.github/workflows/publish-pypi.yml`. It uses GitHub OIDC rather than a stored
PyPI API token and publishes only an existing tag whose `vX.Y.Z` value matches
`pyproject.toml`.

## Current status

- Project: [ragops on PyPI](https://pypi.org/project/ragops/)
- First Trusted Publishing release: `1.6.0`
- Current verified release: `1.8.0`
- GitHub environment: `pypi`
- Publisher: `thangldw/ragops`, workflow `publish-pypi.yml`
- Verification: 1.8.0 wheel and sdist present; clean install and
  credential-free proposal-review demo pass

## One-time owner setup

1. Confirm ownership of the `ragops` project on PyPI.
2. Create a GitHub environment named `pypi`. Add required reviewers if desired.
3. In PyPI Trusted Publishers, configure:
   - Owner: `thangldw`
   - Repository: `ragops`
   - Workflow: `publish-pypi.yml`
   - Environment: `pypi`
4. Keep the workflow's `id-token: write` permission scoped to the publish job.

GitHub's current OIDC guidance is linked from the
[PyPI Trusted Publishing documentation](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-pypi).

## Publish an accepted tag

1. Open **Actions → Publish package to PyPI → Run workflow**.
2. Enter an existing tag such as `v1.8.0`.
3. Approve the `pypi` environment when protection rules require it.
4. After success, install in a clean environment and compare the installed
   version and wheel hash with the GitHub Release asset.

The workflow checks out the tag, verifies tag/package version parity, rebuilds
the distributions, and publishes with a commit-pinned PyPA action. It does not
run automatically on every GitHub Release, preventing an unconfigured or
unreviewed registry publication.

## Rollback rule

PyPI releases are immutable. Do not overwrite or delete a bad artifact as the
normal correction path. Yank the affected version when appropriate, fix the
repository, and publish a new patch version with a changelog entry.
