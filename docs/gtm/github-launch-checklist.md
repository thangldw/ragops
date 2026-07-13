# GitHub launch checklist

This file records the repository-owner actions that cannot be completed by a
code push. Use the exact copy below so discovery claims stay aligned with the
public product contract.

## Repository About — complete

- **Description:** `From RAG change to explainable PASS/BLOCK release evidence—locally, in five minutes.`
- **Website:** `https://thangldw.github.io/ragops/`
- **Topics:** `ai-evaluation`, `rag`, `llm`, `agents`, `red-team`,
  `observability`, `llmops`, `python`, `github-actions`, `japanese`
- **Social preview:** `docs/demo/social-preview.png` remains ready for manual
  upload because the current automation surface cannot attach repository
  settings files.
- Discussions: enabled.

## Starter issues — complete

- [#1 GitLab CI recipe](https://github.com/thangldw/ragops/issues/1)
  (`help wanted`).
- [#2 proposal-review demo](https://github.com/thangldw/ragops/issues/2)
  (`good first issue`).
- [#3 safe PR comment design](https://github.com/thangldw/ragops/issues/3)
  (`help wanted`).

The former support-triage and answer-length proposals were implemented in the
v1.7 slice rather than opened as already-completed issues.

## Owner-only external gates

- GitHub Release v2.4.0 and the refreshed GitHub Pages showcase are publicly
  verified without GitHub Actions.
- PyPI v2.4.0 is publicly verified; its wheel and source archive match the
  GitHub Release SHA-256 values byte-for-byte, and a clean install/demo passes.
- Recruit a design partner and record observed adoption/ROI separately from
  synthetic benchmark results.
- Configure branch protection and security settings under the owner's chosen
  collaboration policy.
