# GitHub launch checklist

This file records the repository-owner actions that cannot be completed by a
code push. Use the exact copy below so discovery claims stay aligned with the
public product contract.

## Repository About

- **Description:** `Dependency-free evaluation and red-team release gates for RAG and agent systems.`
- **Website:** `https://thangldw.github.io/ragops/`
- **Topics:** `ai-evaluation`, `rag`, `llm`, `agents`, `red-team`,
  `observability`, `llmops`, `python`, `github-actions`, `japanese`
- **Social preview:** `docs/demo/social-preview.png`
- Enable Discussions after support categories and moderation ownership are
  assigned.

## Starter issue: second credential-free demo

**Title:** `[Good first issue] Add a support-triage demo scenario`

**Labels:** `good first issue`, `documentation`, `enhancement`

**Body:**

> Add a second scenario selectable by `ragops demo` that models support-ticket
> triage. Keep it credential-free and synthetic. Include a passing baseline,
> an intentionally blocked candidate, unit/integration coverage, and a README
> command. Do not change metric meaning or the default Japanese troubleshooting
> scenario. Before implementation, propose the fixture IDs and expected gates
> in the issue.

## Starter issue: answer-length budget evaluator

**Title:** `[Good first issue] Propose a deterministic answer-length budget evaluator`

**Labels:** `good first issue`, `evaluation`, `help wanted`

**Body:**

> Propose a deterministic evaluator that reports whether an answer exceeds a
> configured length budget. Define whether the unit is Unicode code points,
> words, or bytes; document limitations for Japanese text; add unit and
> negative tests; and show plugin registration. Metric meaning and any critical
> release behavior require owner acceptance before implementation.

## Owner-only external gates

- Create/configure the PyPI project and Trusted Publisher described in
  `docs/engineering/pypi-publishing.md`.
- Choose a v1.6 release boundary after reviewing the changes on `main`.
- Recruit a design partner and record observed adoption/ROI separately from
  synthetic benchmark results.
- Configure branch protection and security settings under the owner's chosen
  collaboration policy.
