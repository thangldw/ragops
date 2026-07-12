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

## Work assignment convention

- Claude Code or Codex implements one issue-sized story at a time.
- The implementer links requirement, ADR, tests, and evidence in the pull request.
- Thang reviews metric meaning, architecture, product fit, and final acceptance.
