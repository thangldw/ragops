# Project charter

## Objective

Deliver a credible open-source v0.1 that proves the core product loop:
scenario → evaluation → evidence → release decision.

## Roles

| Responsibility | Owner |
| --- | --- |
| Product vision and acceptance | Thang |
| Implementation and test support | Codex / Claude Code |
| Architecture decisions | Thang, supported by AI coding tools |
| Final review and release | Thang |

## Milestones

1. **Foundation:** contracts, scenario schema, deterministic runner.
2. **Interfaces:** CLI and HTTP API.
3. **Credibility:** test suite, CI, documentation, sample report.
4. **v0.2:** provider adapters, trace ingestion, richer evaluators.
5. **v0.3:** dashboard, experiment comparison, trend analysis.

## Acceptance criteria for v0.1

- All automated tests pass on Python 3.11 and 3.12.
- Sample scenario produces a passing release decision.
- A secret leak or unapproved external-action claim blocks release.
- CLI writes/prints valid report JSON.
- API contract delegates to the same evaluation engine.

