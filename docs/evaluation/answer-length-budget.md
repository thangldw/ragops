# Answer-length budget evaluator

`answer_length_budget` is a deterministic diagnostic evaluator for workflows
where answers should remain within an application-owned character budget.

## Contract

- Count: `len(response.answer)` in Python Unicode code points.
- Included: whitespace and punctuation.
- Transformation: none; text is not normalized.
- Boundary: a response equal to the configured limit passes.
- Exceeded result: `within_budget = 0` plus one medium-severity
  `answer_length_budget_exceeded` finding.
- Release behavior: diagnostic findings do not independently block release.

## CLI

```bash
ragops evaluate \
  --scenario scenario.json \
  --responses responses.json \
  --evaluator answer_length_budget \
  --answer-length-limit 500
```

The report adds aggregate `answer_length_budget.character_count` and
`answer_length_budget.within_budget` metrics. Case details retain the exact
finding and measured count.

## Python

```python
from ragops.plugins import AnswerLengthBudgetEvaluator

evaluator = AnswerLengthBudgetEvaluator(max_characters=500)
```

## Limitations

Unicode code points are stable and dependency-free, but do not equal model
tokens, bytes, display columns, or user-perceived grapheme clusters. A shorter
answer is not automatically more correct or useful. Promote this diagnostic to
a release policy only through a separately reviewed contract.
