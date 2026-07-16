# Architecture decisions

This document is the current binding decision set. Detailed superseded ADR files
remain available in Git history.

## Core and product boundary

1. `src/ragops/` stays dependency-free and owns evaluation semantics.
2. RAGOps evaluates recorded behavior; it does not own retrieval, generation,
   orchestration, or business actions.
3. Scenarios, traces, deterministic evaluators, regression gates, reports, and
   plugin protocols remain open source under MIT.
4. Reference applications live under `examples/` and integrate through portable
   contracts.

## Contracts and release decisions

1. Public schemas are versioned. Compatible extensions preserve older readers;
   incompatible changes require a new schema version and owner acceptance.
2. Baseline and candidate are evaluated independently before regression policy
   is applied. Candidate absolute failure always blocks comparison.
3. Critical findings are non-compensating and cannot be offset by averages.
4. Response overlays may override a local baseline by case ID but must reject
   cycles, unknown cases, duplicate overrides, and unknown fields.
5. Custom evaluator metrics become release gates only through an explicit
   evaluation policy. Missing or non-finite policy inputs fail closed.
6. External metrics use a versioned provider envelope and preserve producer-
   defined direction, scale, calibration, and meaning.

## Adapters and security

1. CLI, FastAPI, browser, provider, OpenTelemetry, CI, and publisher surfaces
   are adapters; they do not redefine core evaluation behavior.
2. Protected API endpoints fail closed unless an API key is configured or
   explicit insecure local mode is enabled. Request bytes and case collections
   are bounded.
3. Pull-request evaluation remains read-only. Comment publication runs as an
   isolated default-branch workflow, verifies bounded untrusted artifacts, and
   never executes pull-request content.
4. Artifact and comment enumeration are bounded. Ambiguity, expiry, rate limits,
   or metadata mismatch publish nothing and never weaken the canonical gate.

## Evidence and operations

1. Lexical groundedness is transparent overlap evidence, not entailment.
2. Unicode answer budgets count Python code points and remain diagnostic unless
   a reviewed policy promotes them.
3. Pilot observations are pseudonymous, deterministic, and separate measured
   outcomes from economic assumptions.
4. Release artifacts are built once, checksum-verified, clean-installed, and
   promoted without rebuilding. Local-token publication must record that it is
   not OIDC provenance.
5. Git history and `CHANGELOG.md` are the project archive. Repository HEAD keeps
   only current guidance and current acceptance evidence.
6. Intermediate subfeatures remain under `Unreleased`. Tags and package
   publication occur only for an owner-approved major product milestone, not
   for each implementation checkpoint.
7. The reset public line uses two-part GitHub milestone tags (`v1.0`, `v1.1`)
   and three-part Python package versions (`1.0.0`, `1.1.0`). The owner-approved
   reset removes pre-baseline release listings while Git commit history remains
   the engineering archive.

## Compatibility rule

Any change to a schema, metric meaning, release-gate behavior, or open-core
boundary requires a new decision record and explicit owner review. Presentation
and documentation corrections remain compatible when runtime contracts do not
change.

## Accepted in 1.0.0: statistical regression milestone

Opt-in fixed and sequential paths accept versioned replay bundles of per-case,
per-repeat metrics. Fixed comparison applies one-sided paired hierarchical
bootstrap bounds. Sequential comparison uses predeclared looks with Bonferroni
error spending across looks, directions, and gated metrics. The existing
`evaluate` and `compare` contracts remain unchanged.

The proposed contract keeps recorded statistical evidence and decision
semantics in the dependency-free core. Model execution, provider SDKs,
OpenTelemetry collection, signing, and publication remain adapters. Baseline
and candidate must use the same scenario ID and digest, dataset, evaluator,
environment, case coverage, and metric names; application, model, model
configuration, and recorded evidence provenance may differ. Environment or
evaluator changes make a model-regression comparison fail closed.
Insufficient distinct-case evidence blocks with a named policy reason rather
than becoming an input error.

Evaluator drift uses the same frozen dataset, evidence, application, model,
configuration, and environment with different evaluator provenance. Its
two-sided equivalence interval must remain within an explicit tolerance.
Provenance diagnosis labels isolated axes but never claims causality for a
confounded comparison.

Accepted baseline manifests bind exact replay-bundle and policy bytes with
SHA-256. Detached SSH signatures are optional adapters and use the
`ragops-baseline` namespace. Integrity verification remains available without
SSH; signature verification establishes identity when an approved
allowed-signers file is supplied.

The owner accepted these experimental schemas and gates as the 1.0.0 public
commitment on 2026-07-15. Live provider calls, hosted storage, and automatic
causal decomposition remain outside this decision.

## Proposed for the next milestone: tagged evidence contracts

Two opt-in deterministic plugins make named Failure Zoo evidence more direct
without changing default evaluation. `source_freshness` applies only to cases
tagged `freshness` and compares supplied citation IDs with the exact current IDs
declared by the scenario. `abstention_contract` applies only to cases tagged
`abstain` and combines required-citation coverage with transparent lexical
overlap against the declared evidence. Untagged cases return a neutral score.

These metrics remain diagnostic unless an evaluation policy gates them. A
contract violation emits a high finding, so the caller must opt into both the
evaluator and an appropriate finding policy. Neither evaluator infers document
dates, semantic entailment, or safe abstention. This compatible plugin addition
requires owner acceptance before inclusion in the next public milestone.
