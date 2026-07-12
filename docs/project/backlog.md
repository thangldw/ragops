# Prioritized backlog

## Now — milestone M1

M1 is accepted in `docs/project/m1-acceptance.md`. The completed stories remain
below as a traceable record; active implementation moves to M2.

| ID | Story | Acceptance evidence |
| --- | --- | --- |
| BENCH-01 | Define scenario case metadata contract | ADR, schema proposal, compatibility tests |
| BENCH-02 | Author 30+ Japanese cases across the published taxonomy | Reviewed fixtures and coverage report |
| EVAL-01 | Measure citation precision and completeness | Unit tests and calibrated examples |
| EVAL-02 | Add claim-level groundedness plugin | Human-labeled fixture comparison and limitations |
| RED-01 | Define portable attack-pack contract | Schema, loader, and negative tests |
| RED-02 | Add injection, leakage, and excessive-agency packs | Category coverage report and blocked fixtures |
| UX-01 | Add per-case comparison drill-down to HTML | Screenshot and interaction test |

## Next — milestone M2

M2 is accepted in `docs/project/m2-acceptance.md`. The recorded stories remain
below; active implementation moves to the FDE showcase and team workflow.

| ID | Story | Acceptance evidence |
| --- | --- | --- |
| REF-01 | Build minimal Japanese reference RAG/agent | Reproducible local setup and trace export |
| TRACE-01 | Extend trace metadata without breaking 0.3 fixtures | Schema and migration/compatibility tests |
| ADAPT-01 | Add generic HTTP trace adapter | Example integration and failure handling tests |
| DEMO-01 | Record improvement and regression experiment | Baseline, candidate, report, and decision note |

## Later — milestones M3–M5

- M3 portfolio page and presentation assets are accepted.
- M4 local team workflow is accepted.
- Design-partner discovery and observed workflow validation.
- Shared hosted workspace only after collaboration demand is demonstrated.

## Adoption backlog — v1.5 and beyond

These are suitable seeds for real GitHub issues. Apply `good first issue` only
when the acceptance criteria are small enough for a first-time contributor.

| ID | Suggested labels | Story | Acceptance evidence |
| --- | --- | --- | --- |
| DX-01 | good first issue, documentation | Add a second `ragops demo` scenario for support triage | Credential-free bundle, test, README example |
| EVAL-03 | good first issue, evaluator | Add a deterministic answer-length budget evaluator | Unit/negative tests and plugin documentation |
| REPORT-02 | help wanted, reporting | Add accessible print styles to the standalone HTML report | Browser capture and HTML regression test |
| INTEG-01 | help wanted, integration | Publish a copyable GitHub Actions release-gate recipe | Passing/failing fixture example and setup guide |
| TRACE-02 | help wanted, integration | Add an OpenTelemetry span-to-trace example | Synthetic exporter fixture and compatibility test |
| DOCS-02 | good first issue, documentation | Add a framework-neutral “export your first trace” tutorial | Five-minute walkthrough with synthetic data |
| DIST-01 | release | Configure PyPI Trusted Publishing and publish synchronized release | Owner-configured environment, CI, release notes, install verification |

Completed on `main` after v1.5.0: `DX-01`, `EVAL-03`, `REPORT-02`, `INTEG-01`,
`TRACE-02`, and `DOCS-02`.
`DIST-01` is complete: PyPI project ownership, the `pypi` environment, active
Trusted Publisher, synchronized release artifacts, and clean-install verification
are recorded.

## Contributor backlog — after v1.7 implementation

| ID | GitHub issue | Story | Status |
| --- | --- | --- | --- |
| INTEG-02 | [#1](https://github.com/thangldw/ragops/issues/1) | Add a copyable GitLab CI release-gate recipe | Complete; issue closed |
| DX-02 | [#2](https://github.com/thangldw/ragops/issues/2) | Add a credential-free proposal-review demo | Complete; issue closed |
| INTEG-03 | [#3](https://github.com/thangldw/ragops/issues/3) | Design safe pull-request comment publishing | Design complete; issue closed; implementation deferred |

## Work assignment convention

- Claude Code or Codex implements one issue-sized story at a time.
- The implementer links requirement, ADR, tests, and evidence in the pull request.
- Thang reviews metric meaning, architecture, product fit, and final acceptance.
