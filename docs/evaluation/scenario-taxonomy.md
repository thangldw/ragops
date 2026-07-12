# Japanese troubleshooting benchmark taxonomy

The reference benchmark contains 30 synthetic cases. This establishes coverage
discipline, not external validity; customer-derived and human-reviewed cases are
still required before making production-quality claims.

| Family | Minimum cases | Purpose |
| --- | ---: | --- |
| Direct procedure | 4 | Retrieve and cite an explicit action |
| Escalation decision | 4 | Apply threshold and approval policy |
| Multi-document synthesis | 4 | Combine manual, incident, and policy evidence |
| Clarification / abstention | 3 | Avoid unsupported answers when context is missing |
| Conflicting or stale evidence | 3 | Prefer authoritative/current source |
| Product/model disambiguation | 3 | Prevent similar-model contamination |
| Permission leakage | 3 | Enforce role-appropriate evidence |
| Prompt injection | 3 | Ignore malicious instructions in retrieved content |
| Consequential action | 3 | Require human approval and preserve auditability |

Each case should document expected evidence, failure mode, severity, language,
and whether it is deterministic, judge-assisted, or human-reviewed.

Inspect current coverage with:

```bash
ragops inspect --scenario scenarios/japanese_troubleshooting/benchmark-v0.2.json
```
