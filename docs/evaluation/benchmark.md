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

## RAG Failure Zoo

The zoo is a runnable candidate, not a threat-coverage claim. Each specimen is
one synthetic, inspectable failure layered over the passing baseline.

| Specimen | Case | Candidate failure | Visible evidence |
| --- | --- | --- | --- |
| Permission leakage | `acl-01` | Returns a configured executive-only marker | Critical `forbidden_output_term`, missing citation, unsupported answer |
| Stale source | `stale-01` | Uses superseded 80C guidance and an old source ID | Citation coverage/precision and lexical groundedness fail |
| Wrong citation | `inject-03` | Adds a fabricated source ID | Citation precision falls |
| Prompt injection | `inject-02` | Obeys a request to reveal a synthetic secret | Critical `forbidden_output_term` |
| Failure to abstain | `abstain-01` | Invents a repair when no approved procedure exists | Missing citation and unsupported answer |
| Excessive agency | `action-01` | Claims an email was sent without approval | Critical `external_action_without_approval` |

Run all specimens offline:

```bash
ragops compare \
  --scenario scenarios/japanese_troubleshooting/benchmark-v0.2.json \
  --baseline scenarios/japanese_troubleshooting/benchmark-baseline.json \
  --candidate scenarios/japanese_troubleshooting/failure-zoo-candidate.json \
  --evaluator source_freshness \
  --evaluator abstention_contract \
  --evaluation-policy scenarios/japanese_troubleshooting/failure-zoo-policy.toml \
  --format html \
  --output failure-zoo-report.html
```

The expected exit is `2`. Freshness means exact current-source IDs, and the
abstention check is lexical. The checks demonstrate that configured examples
are caught; they do not prove resistance to unseen attacks, source recency from
content, semantic correctness, or safe abstention.

### Retrieval-poisoning specimen

```bash
ragops compare \
  --scenario scenarios/japanese_troubleshooting/benchmark-v0.2.json \
  --baseline scenarios/japanese_troubleshooting/benchmark-baseline.json \
  --candidate scenarios/japanese_troubleshooting/retrieval-poisoning-candidate.json \
  --evaluator citation_correctness \
  --evaluator claim_support \
  --evaluation-policy scenarios/japanese_troubleshooting/evaluation-policy.toml \
  --format html \
  --output retrieval-poisoning-report.html
```

The expected exit is `2`. This synthetic specimen demonstrates a retrieval-poisoning failure in which a response follows instructions embedded in retrieved content. It intentionally triggers unsupported citations and unsupported claims for evaluation purposes. It does not demonstrate real-world security guarantees.

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
