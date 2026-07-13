# Requirements v2.0 — trustworthy extensible release gates

## User stories

1. As a release owner, I want selected evaluator metrics to be enforceable so
   that plugin evidence can block a release instead of remaining diagnostic.
2. As a reviewer, I want evaluate and compare to run the same evaluators and
   absolute gates so that the decision does not depend on the command used.
3. As a CI owner, I want malformed numeric input to fail closed so that `NaN`,
   infinity, negative budgets, or invalid ratios cannot bypass a gate.
4. As an API operator, I want authentication and payload limits to be explicit
   so that a sample deployment cannot silently expose mutation endpoints.
5. As a benchmark user, I want synthetic evidence labeled honestly so that a
   harness fixture is not mistaken for proof of Japanese semantic quality.

## Public contract impact

- Add an optional evaluation-policy TOML contract with canonical metric names,
  minimum/maximum thresholds, and a finding-severity floor.
- Add evaluator selection to `compare`; the same evaluator instances and
  evaluation policy are applied to baseline and candidate.
- Add custom metric deltas to comparison reports when evaluators are selected.
- Reject non-finite numbers, out-of-range ratios, negative latency/cost, and
  invalid policy thresholds. Previously valid inputs and omitted policy retain
  their results and exit codes.
- Require an API key by default for protected endpoints. Local unauthenticated
  use requires explicit `RAGOPS_INSECURE_DEV_MODE=true`; Compose binds to
  localhost by default.

## Acceptance criteria

1. A configured plugin metric below its minimum or above its maximum produces a
   named failed gate and exit code 2.
2. `fail_on_severity = "high"` blocks high and critical findings while the
   backwards-compatible default remains critical.
3. `evaluate` and `compare` accept the same evaluator options and produce the
   same candidate absolute-gate decision.
4. Comparison deltas contain every numeric metric shared by baseline and
   candidate, including selected custom evaluator metrics.
5. Unknown policy metrics, missing evaluator output, duplicate evaluators,
   invalid directions, invalid severity, and non-finite metric output fail with
   actionable contract errors.
6. Scenario and response loaders reject non-finite values, ratios outside
   `[0, 1]`, booleans used as numbers, and negative latency/cost.
7. Protected API endpoints return 503 when no authentication mode is configured,
   401 for a missing or wrong configured key, and allow explicit insecure dev
   mode only when the key is absent.
8. API request bytes and case/response counts are bounded with documented
   defaults and negative tests.
9. The Japanese troubleshooting fixture is labeled as a synthetic release-gate
   benchmark; documentation does not claim semantic Japanese validation.
10. Existing fixtures, default CLI behavior, deterministic reports, offline
    operation, Ruff, and the full test suite remain green.

## Non-goals

- Semantic entailment or provider-backed judging in the dependency-free core.
- Changing the meaning of existing built-in metrics.
- Sandboxing third-party evaluator code.
- Hosted rate limiting, SSO/RBAC, tenant isolation, HA, or penetration testing.
- Claiming real Japanese model quality, customer adoption, or ROI.
