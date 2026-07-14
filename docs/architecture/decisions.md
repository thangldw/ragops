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

## Compatibility rule

Any change to a schema, metric meaning, release-gate behavior, or open-core
boundary requires a new decision record and explicit owner review. Presentation
and documentation corrections remain compatible when runtime contracts do not
change.
