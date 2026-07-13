# Requirements v2.1 — portable external metric evidence

## User stories

1. As a release owner already using Ragas, DeepEval, Langfuse, or an internal
   judge, I want to import per-case scores without replacing my evaluator stack.
2. As a CI owner, I want imported scores to pass through the same deterministic
   policy and comparison engine as built-in metrics.
3. As a reviewer, I want provider identity and canonical metric names visible in
   reports so that the source of a release gate is auditable.
4. As an adopter, I want a copyable PR publisher recipe whose workflow-name
   allowlist and trust boundary are explicit.

## Public contract impact

- Add external metric envelope schema 0.1 with provider, per-case metric maps,
  and exact scenario coverage.
- Add `--external-metrics` to `evaluate` and repeatable baseline/candidate-shared
  external metric inputs to `compare`.
- Aggregate imported metrics under `<provider>.<metric>` and expose them to the
  existing evaluation policy without changing their meaning.
- Add a downstream-repository publisher recipe and setup guide. The privileged
  publisher remains isolated from untrusted PR execution.

## Acceptance criteria

1. Envelope provider is one of `ragas`, `deepeval`, `langfuse`, or `custom` and
   all case IDs are unique.
2. Imported metric names are non-empty, values are finite numbers, booleans are
   rejected, and every scenario case has exactly one metric record.
3. Evaluate can gate an imported metric using the existing minimum/maximum
   evaluation policy.
4. Compare accepts distinct baseline and candidate envelopes from the same
   provider with identical metric names and reports their deltas.
5. Provider, coverage, missing cases, extra cases, and metric-set mismatch fail
   closed with actionable contract errors.
6. Existing CLI and Python behavior is unchanged when no external metrics are
   supplied.
7. The downstream publisher recipe documents the exact source workflow name,
   permissions, artifact contract, marker behavior, and fork limitation.
8. Ruff, unit/negative/CLI/workflow tests, and the full Python matrix pass.

## Non-goals

- Importing unstable native vendor export formats directly into the core.
- Installing Ragas, DeepEval, Langfuse, model SDKs, or network clients.
- Reinterpreting, normalizing, calibrating, or comparing semantically different
  third-party metrics.
- Running provider-backed judges inside the release gate.
- Claiming external framework endorsement or production adoption.
