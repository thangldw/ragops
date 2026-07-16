# Current product requirement

## User story

As an engineer releasing a stochastic RAG or AI system, I can collect repeated
recorded metrics, separate known provenance changes, and make an offline
PASS/BLOCK decision using both effect size and uncertainty. I can replay and
audit the same evidence without a hosted service or provider SDK in the core.

## Contract impact

This milestone adds opt-in replay-bundle, repeated-run plan, statistical report,
sequential report, evaluator-drift, provenance-diagnosis, and accepted-baseline
manifest contracts. It adds CLI/API adapters and a reusable read-only GitHub
statistical gate. Existing `evaluate`, `compare`, schemas, metric meanings, and
deterministic PASS/BLOCK behavior remain compatible.

The dependency-free core continues to evaluate recorded evidence only. Model
execution, provider SDKs, OpenTelemetry collection, SSH signing, CI, and PR
publication remain adapters.

The Unreleased flagship-adoption slice adds opt-in source-freshness and
abstention-contract evaluators over existing scenario tags and evidence. It
does not change default evaluation behavior or any existing metric meaning.

## Acceptance criteria

- Fixed-sample comparison applies one-sided absolute and non-inferiority bounds
  over paired cases with repeats resampled within cases.
- Sequential evaluation uses predeclared looks and family-wise Bonferroni error
  spending; it can PASS or BLOCK early and otherwise fails closed.
- Distinct cases, not repeats, satisfy `minimum_cases`; insufficient evidence
  produces a named policy block.
- Replay provenance records scenario, dataset, evidence, evaluator,
  application, model, configuration, and environment identifiers.
- Provenance diagnosis distinguishes model regression, evaluator drift,
  dataset drift, infrastructure noise, stochastic output variance, repeated
  measurement variance, and confounded comparisons.
- Evaluator drift requires frozen evidence and isolates the evaluator axis with
  a two-sided equivalence interval.
- Repeated-run collection is bounded, command-explicit, shell-free, resumable,
  atomically checkpointed, and able to stop on a sequential decision.
- Accepted baseline manifests bind bundle and policy bytes; optional detached
  SSH signatures verify owner identity offline.
- Ragas, DeepEval, and OpenTelemetry adapters preserve recorded producer scores
  without changing direction, scale, calibration, or meaning.
- CLI, authenticated bounded API, reusable GitHub workflow, Markdown/JSON
  reports, PASS/BLOCK fixtures, schemas, tests, and current guidance agree.
- `source_freshness` checks exact current-source IDs only for cases tagged
  `freshness`; `abstention_contract` checks cited lexical support only for cases
  tagged `abstain`; untagged cases remain neutral.
- Ruff, full tests, schema checks, affected CLI/API paths, package build, clean
  install, and security review pass before owner acceptance.

## Non-goals

- No claim that a generic provenance diagnosis proves causality when more than
  one causal axis changed.
- No ordinary fixed-sample confidence interval may be repeatedly inspected as a
  sequential stopping rule.
- No provider score is reinterpreted as ground truth or silently recalibrated.
- No source date is inferred and no lexical abstention score is described as
  semantic understanding or proof that an answer safely abstains.
- No hosted-service, live credential, customer-data, or production-security
  claim is introduced.
- No tag, package publication, or public deployment occurs for intermediate
  subfeatures. Changes accumulate under `Unreleased` and are released only as
  an owner-approved major product milestone.
