# Evaluation strategy

## Evaluation pyramid

1. Contract validity and response coverage.
2. Deterministic safety and policy rules.
3. Retrieval, citation, quality, latency, and cost metrics.
4. Optional semantic/model judges with calibration evidence.
5. Human review and online workflow outcomes.

## Release-decision rule

The candidate must pass absolute thresholds and regression tolerances. Critical
policy findings are non-compensating: higher average quality cannot offset one.

## Calibration

Every non-trivial evaluator needs labeled examples, documented failure modes,
and agreement analysis against qualified human reviewers. LLM-as-judge outputs
must record model and prompt versions and be treated as measurements with
uncertainty, not ground truth.

The open-source core includes two transparent evaluator baselines:

- `citation_correctness` checks supplied citation IDs against the case evidence
  contract and reports unsupported citations.
- `claim_support` splits answers into claims and measures lexical evidence
  support. It is explicitly not semantic entailment.

Both expose aggregate and per-case plugin metrics. Production semantic judges
must be separately calibrated against qualified human labels.

## Outcome metrics

Offline answer quality does not prove business impact. Reference deployments
should also propose adoption, task completion, escalation, time saved, and
cost-per-successful-task measures.
