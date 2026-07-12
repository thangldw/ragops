# ADR 0013: Add a demo catalog and Unicode code-point budget evaluator

- Status: Accepted by product owner continuation request
- Date: 2026-07-13

## Context

The single troubleshooting demo makes adoption easy but can look domain-bound.
Teams also need a transparent way to identify answers that exceed an
application-owned length budget without installing a model tokenizer.

## Decision

Represent credential-free demo bundles in a named catalog. The existing
Japanese troubleshooting bundle remains the default; support triage is an
additive selection.

Add a configurable `answer_length_budget` case evaluator. It counts Python
Unicode code points with `len(response.answer)`, including whitespace and
punctuation and without normalization. It reports average case metrics and a
medium finding when exceeded. It does not add a core threshold or critical
finding, so existing release decisions remain unchanged.

## Compatibility impact

The CLI and plugin surface are extended additively. Existing demo commands,
scenarios, traces, reports, metrics, evaluators, API behavior, and release
policies remain compatible.

## Consequences

- Users can demonstrate the product in a second workflow without credentials.
- Japanese text is counted deterministically without English word assumptions.
- Code-point length is not token usage, display width, grapheme count, or a
  measure of semantic quality; documentation must preserve this limitation.
- Future release enforcement would require a separately reviewed policy
  contract rather than silently promoting this diagnostic finding.
