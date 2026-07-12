# Risk register

| Risk | Probability | Impact | Mitigation | Trigger |
| --- | --- | --- | --- | --- |
| “RAGOps” is confused with an orchestration framework | Medium | High | Repeat evaluate-not-orchestrate boundary | Requests focus on vector DB features |
| Metrics look rigorous but are semantically weak | High | High | Label lexical baseline; add calibrated evaluators | False passes in benchmark review |
| Red-team claim exceeds actual attack coverage | High | High | Publish taxonomy and coverage limits | External reviewer finds trivial bypass |
| Scenario is too small or synthetic | High | High | 30+ cases and documented fixture method | Demo cannot show failure diversity |
| Open-core boundary alienates contributors | Medium | High | Keep core complete and governance transparent | Key feature moves behind hosted tier |
| Schema churn breaks adopters | Medium | High | Version contracts and migration tests | Public field changes without ADR |
| AI-generated code lowers maintainability | Medium | Medium | Small changes, tests, owner review | Large unexplained refactors |
| Portfolio claims exceed measured evidence | Medium | High | Separate targets, simulations, and observations | Illustrative metric presented as result |

Review this register at every milestone and after any security or compatibility
incident.

