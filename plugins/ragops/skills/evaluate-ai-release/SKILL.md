---
name: evaluate-ai-release
description: Evaluate a RAG system or AI-agent release against an accepted baseline, diagnose regressions, and produce explainable PASS, WARN, or BLOCK evidence. Use for candidate traces, RAG evaluation scenarios, model or prompt changes, release gates, citation regressions, abstention checks, and pre-release AI quality reviews.
---

# Evaluate an AI release

Use RAGOps as a deterministic evaluator. It runs through the `ragops` command-line tool, which this plugin does not bundle: install it once with `pip install ragops` (Python 3.11+; see https://pypi.org/project/ragops/) and confirm with `ragops --version`. If it is missing, tell the user and ask before installing anything. Treat its result as release evidence, not as proof that a system is universally correct or safe.

## Workflow

1. Identify the scenario, candidate responses or traces, accepted baseline, and policy thresholds. Do not invent missing fixtures.
2. Read `references/commands.md` when selecting the RAGOps command or interpreting exit codes.
3. Inspect inputs for secrets or personal data before running an evaluation. Keep generated reports private unless the user approves sharing.
4. Run the narrowest applicable command with `ragops ...`.
5. Interpret exit code `0` as PASS and exit code `2` as an evaluated BLOCK, not an execution failure. `ragops counterfactual` also returns `3` for INCONCLUSIVE (too few eligible cases): say that nothing was concluded. Treat other nonzero codes as operational errors.
6. Verify generated evidence bundles before using them, then report the decision, failed gates, material metric deltas, provenance limitations, and the smallest next action.

## Beyond a plain comparison

Pick the check that fits the question (details and flags in `references/commands.md`):

- No release policy yet: `policy-suggest` writes a slice-aware policy from an accepted baseline. Present it as a draft for the owner to review, never as approved.
- A bad answer was found in production: `mine` adds flagged logs (thumbs down, low rating, escalated) to the scenario as regression cases.
- Is the answer really based on the evidence: `counterfactual` alters the evidence and re-asks the user's own system (removing support, swapping numbers, dropping a citation, planting an instruction, removing all evidence).
- Do the counterfactual checks work on this data: `counterfactual-selftest` needs no system; run it before trusting a `counterfactual` result, and report `weak` or `too_few_cases` perturbations as unreliable.
- Results differ between runs: `stability` gates the spread of repeated runs.
- Is the scorer trustworthy: `calibrate` (with the user's human labels) reports an accuracy-based confidence band and a suggested threshold; `triage` then routes cases to auto-pass, auto-fail or human review.

## Guardrails

- `counterfactual --answer-command` executes a command and calls the user's system once or more per case. Run only a command the user wrote or explicitly approved, say how many calls to expect (use `--limit` for a first pass), and never point it at production systems with side effects.
- Treat a `counterfactual` flag as a lead: redundant evidence can make a faithful answer look unchanged. Only the toy demo has been measured, so do not describe the test as validated on real systems.
- Do not change a policy or the number of repeats after seeing a failing result in order to get a pass.
- Do not weaken thresholds, replace the accepted baseline, or omit failing cases to obtain a pass.
- Do not claim semantic correctness when only lexical or citation checks were run.
- Do not run provider-backed evaluation unless the user explicitly supplies and authorizes the provider configuration.
- Do not publish, merge, tag, or deploy based only on this skill's output.
- Preserve input artifacts and command parameters in the final evidence so another reviewer can reproduce the result.
- Distinguish synthetic, production-derived, and live production evidence; never infer adoption from the bundled demo.

## Output

Return a concise release recommendation with: `decision`, `evidence`, `failed_gates`, `limitations`, and `next_action`.
