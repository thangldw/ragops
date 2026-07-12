# GitLab CI release gate

Copy `docs/examples/gitlab-ci-ragops.yml` into the target repository's
`.gitlab-ci.yml`, or include the job in an existing pipeline.

The recipe:

- runs only in merge-request pipelines;
- installs a pinned stable RAGOps version from PyPI;
- compares a candidate with an accepted baseline;
- preserves CLI exit `0` for PASS and exit `2` for BLOCK;
- uploads Markdown evidence and the command log with `artifacts.when: always`,
  including failed jobs;
- uses no GitLab API token, provider credential, or write permission.

## Configure inputs

Set these repository-relative variables:

```yaml
variables:
  RAGOPS_VERSION: "1.6.0"
  RAGOPS_SCENARIO: "evaluation/scenario.json"
  RAGOPS_BASELINE: "evaluation/baseline.json"
  RAGOPS_CANDIDATE: "evaluation/candidate.json"
  RAGOPS_POLICY: "ragops.toml"
```

Leave `RAGOPS_POLICY` empty when no regression-policy file is needed. All paths
are quoted before reaching the shell command.

## Expected behavior

- PASS: job succeeds and keeps both artifacts.
- BLOCK: job fails with exit `2` and keeps both artifacts for review.
- Contract/setup error: job fails and synthesizes a Markdown error report from
  the command log when no normal report exists.

The failed job is the release gate; do not add `allow_failure: true` unless the
team intentionally wants advisory-only evaluation.
