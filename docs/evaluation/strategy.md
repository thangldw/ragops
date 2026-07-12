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

## Outcome metrics

Offline answer quality does not prove business impact. Reference deployments
should also propose adoption, task completion, escalation, time saved, and
cost-per-successful-task measures.

