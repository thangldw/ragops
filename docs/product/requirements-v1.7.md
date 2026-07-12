# Requirements v1.7 — broader adoption proof

## User stories

1. As an evaluator exploring RAGOps, I want a second credential-free demo so
   that I can see the release-gate pattern outside troubleshooting.
2. As an AI engineer, I want a deterministic answer-length budget evaluator so
   that overly verbose responses are visible in reports without requiring a
   tokenizer or provider SDK.
3. As a presales engineer, I want a proposal-review demo so that the release
   contract is visible in a business-facing workflow.
4. As a GitLab user, I want a copyable merge-request job that preserves RAGOps
   evidence on both PASS and BLOCK.
5. As a repository owner, I want a reviewed PR-comment design before granting
   any workflow write permission.

## Public contract impact

- Add `ragops demo --scenario support-triage`; retain
  `japanese-troubleshooting` as the default.
- Add the `answer_length_budget` evaluator and
  `--answer-length-limit` CLI option for evaluation commands.
- Add `proposal-review` to the credential-free demo catalog.
- Add a GitLab CI recipe and a least-privilege PR-comment design outside the
  evaluation core.
- Report `character_count` and `within_budget` as plugin metrics and a
  non-critical `answer_length_budget_exceeded` finding when over budget.
- Do not change scenario, trace, response, report, API, regression-policy, or
  existing evaluator semantics.

## Acceptance criteria

1. Both demos produce a credential-free bundle with passing baseline,
   intentionally blocked candidate, Markdown evidence, and HTML evidence.
2. Omitting `--scenario` produces the original Japanese troubleshooting demo.
3. Answer length is Python Unicode code-point length with no normalization;
   whitespace and punctuation count.
4. A positive integer limit is required. Equal-to-limit passes; over-limit
   emits metrics and one medium-severity finding.
5. The evaluator is deterministic, dependency-free, available from Python and
   CLI, and does not independently change the report release decision.
6. Unit, negative, CLI, compatibility, and full-suite tests pass.
7. Proposal review uses only synthetic requirements and blocks an unsupported,
   uncited candidate while preserving the original default demo.
8. The GitLab recipe runs on merge requests, preserves exit 0/2, and uploads
   report and command-log artifacts with `when: always`.
9. The PR-comment design separates untrusted evaluation from any future
   write-enabled publisher, forbids executing PR artifacts, and defines
   idempotent comment updates.

## Non-goals

- Tokenizer-specific budgets, grapheme-cluster counting, or semantic concision.
- Adding a new scenario field or core release threshold.
- Replacing human review of answer usefulness.
- Claiming the synthetic support scenario represents customer validation.
- Shipping a write-enabled PR-comment workflow before a separate implementation
  review.
