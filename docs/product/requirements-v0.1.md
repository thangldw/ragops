# Product requirements — v0.1

## User story

As an AI engineer, I want to evaluate recorded responses against a versioned
scenario so that CI can block a release when quality, cost, latency, or safety
requirements regress.

## Functional requirements

1. Load a scenario containing cases, thresholds, budgets, and red-team rules.
2. Load recorded responses independently from the scenario.
3. Evaluate citation coverage and evidence-supported answer terms.
4. Evaluate latency and cost budgets.
5. Detect configured sensitive terms in outputs.
6. Detect external-action claims when human approval is required.
7. Return per-case evidence, aggregate metrics, and a release decision.
8. Provide Python, CLI, and HTTP entry points using the same engine.

## Non-functional requirements

- Runs offline with no API key.
- A scenario result is deterministic for identical inputs.
- Invalid input fails with a useful error.
- Report format is JSON serializable and versioned.
- Core package has no runtime dependencies.

## Release gate

A run passes only when all aggregate thresholds and budgets pass and there are
no critical red-team findings.

## Explicitly out of scope

- Document ingestion and generation orchestration.
- Vector database or retrieval implementation.
- LLM-as-judge.
- Hosted dashboard, authentication, and multi-tenancy.
- Real customer or FPT data.

