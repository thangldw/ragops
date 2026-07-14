# Synthetic benchmark

## Scope

The Japanese troubleshooting suite contains 30 synthetic questions across nine
failure families. It validates release-gate behavior and fixture coverage; it
does not establish model quality or customer impact.

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
attack metadata across eight categories.

## Recorded results

| Metric | Baseline | Regressed | Adversarial |
| --- | ---: | ---: | ---: |
| Citation coverage | 1.0000 | 0.9333 | 0.9333 |
| Citation precision | 1.0000 | 0.9167 | 0.9167 |
| Lexical groundedness | 1.0000 | 0.9333 | 0.8556 |
| Average latency | 966.67 ms | 1326.67 ms | 966.67 ms |
| Average cost | $0.0097 | $0.0193 | $0.0097 |
| Critical findings | 0 | 0 | 5 |
| Decision | PASS | BLOCK | BLOCK |

## Reproduce

```bash
ragops evaluate \
  --scenario scenarios/japanese_troubleshooting/benchmark-v0.2.json \
  --responses scenarios/japanese_troubleshooting/benchmark-baseline.json

ragops compare \
  --scenario scenarios/japanese_troubleshooting/benchmark-v0.2.json \
  --baseline scenarios/japanese_troubleshooting/benchmark-baseline.json \
  --candidate scenarios/japanese_troubleshooting/benchmark-regressed.json
```

The comparison intentionally exits `2`. Answers mirror synthetic evidence;
lexical groundedness is not entailment, and the attack metadata does not prove
production security.
