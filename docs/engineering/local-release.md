# Release without GitHub Actions

Use this only while GitHub Actions is unavailable. Run from a clean release
commit with Python 3.11+ and `gh` authenticated.

```bash
python -m pip install -e '.[dev]' build cyclonedx-bom==7.3.0 twine
python scripts/local_release.py verify --tag vX.Y.Z
python scripts/local_release.py publish-github --tag vX.Y.Z --yes
```

The first command runs all required local gates and writes `dist/` artifacts,
`SHA256SUMS`, an SBOM, and `LOCAL_RELEASE_EVIDENCE.json`. The second creates and
pushes the annotated tag, then creates the GitHub Release directly with `gh`.

PyPI cannot use the repository's GitHub OIDC Trusted Publisher from a local
machine. If PyPI publication cannot wait, create a project-scoped token, expose
it only for this command, and rotate/revoke it afterwards:

```bash
read -s PYPI_API_TOKEN && export PYPI_API_TOKEN
python scripts/local_release.py publish-pypi --tag vX.Y.Z --yes
unset PYPI_API_TOKEN
```

The PyPI phase downloads and verifies the GitHub Release artifacts before
uploading them; it never rebuilds. Do not paste tokens into chat, shell history,
configuration files, or repository secrets.

Pause quota-consuming workflows with `gh workflow disable <workflow-file>` and
restore them later with `gh workflow enable <workflow-file>`. Keep manual notes
of every disabled workflow.
