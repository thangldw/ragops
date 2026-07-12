# Japanese troubleshooting benchmark report — v0.2

## Scope

This synthetic benchmark contains 30 Japanese questions across nine enterprise
troubleshooting and safety families. It evaluates release-gate behavior; it is
not evidence of model quality or customer production impact.

## Coverage

| Family | Cases |
| --- | ---: |
| Direct procedure | 4 |
| Escalation decision | 4 |
| Multi-document synthesis | 4 |
| Clarification and abstention | 3 |
| Conflicting or stale evidence | 3 |
| Model disambiguation | 3 |
| Permission leakage | 3 |
| Prompt injection | 3 |
| Consequential action | 3 |

The suite contains 14 critical, 13 high, and 3 medium cases. Nine cases carry
explicit attack metadata across eight attack categories.

## Reproducible results

| Metric | Baseline | Regressed | Adversarial |
| --- | ---: | ---: | ---: |
| Citation coverage | 1.0000 | 0.9333 | 0.9333 |
| Citation precision | 1.0000 | 0.9167 | 0.9167 |
| Lexical groundedness | 1.0000 | 0.9333 | 0.8556 |
| Average latency | 966.67 ms | 1326.67 ms | 966.67 ms |
| Average cost | $0.0097 | $0.0193 | $0.0097 |
| Critical findings | 0 | 0 | 5 |
| Release decision | PASS | FAIL | FAIL |

The regressed candidate is blocked by citation coverage, citation precision,
groundedness, latency, and cost gates. The adversarial candidate is blocked by
absolute citation gates and critical secret-leak/excessive-agency findings.

## Reproduce

```bash
ragops evaluate \
  --scenario scenarios/japanese_troubleshooting/benchmark-v0.2.json \
  --responses scenarios/japanese_troubleshooting/benchmark-baseline.json

ragops compare \
  --scenario scenarios/japanese_troubleshooting/benchmark-v0.2.json \
  --baseline scenarios/japanese_troubleshooting/benchmark-baseline.json \
  --candidate scenarios/japanese_troubleshooting/benchmark-regressed.json

ragops evaluate \
  --scenario scenarios/japanese_troubleshooting/benchmark-v0.2.json \
  --responses scenarios/japanese_troubleshooting/benchmark-adversarial.json
```

The two failing commands intentionally return exit code `2`.

## Limitations and next evaluation work

- Answers mirror synthetic evidence, so the passing score is a harness test.
- Lexical groundedness does not establish entailment or semantic correctness.
- ACL and injection metadata describe coverage but do not yet execute a target
  application through the portable attack pack.
- Claim-level and citation-entailment evaluators require human-labeled fixtures
  and calibration before production claims.

