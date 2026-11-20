# RAGOps command selection

- Inspect a scenario: `ragops inspect --scenario PATH`
- Evaluate candidate responses: `ragops evaluate --scenario PATH --responses PATH`
- Compare candidate and baseline: run `ragops compare --help` and provide the exact required paths.
- Generate a credential-free evidence bundle: `ragops demo --profile engineer --output OUTPUT_DIR`
- Verify an evidence bundle: `ragops evidence verify --bundle OUTPUT_DIR/evidence`
- Explain a canonical decision: `ragops explain --input OUTPUT_DIR/decision.json`

Further checks (run each with `--help` first; none needs a network or provider unless noted):

- Draft a release policy from a baseline: `policy-suggest --scenario PATH --baseline PATH [--margin 0.05] [--min-cases 3] [--output policy.toml]`, then apply it with `gate-v2 --scenario PATH --baseline PATH --candidate PATH --policy policy.toml`.
- Grow the scenario from production failures: `mine --from LOGS --scenario PATH --responses PATH --output NEW_DIR` (writes a new directory; never overwrites).
- Does the answer depend on the evidence: `counterfactual --scenario PATH --responses PATH --answer-command "COMMAND" [--perturbation all] [--limit N]`. Exit `0` PASS, `2` BLOCK, `3` INCONCLUSIVE. This runs the given command, which calls the user's system; see `docs/counterfactual-test.md` in the repository for the protocol and limits.
- Do the checks work on this data: `counterfactual-selftest --scenario PATH --responses PATH` (offline, no system needed). Exit `0` VALID, `2` WEAK, `3` INCONCLUSIVE.
- Repeatability: `stability --bundle RUNS.json [--baseline-bundle OLD.json] [--max-stddev-increase X]` (bundles come from `collect-runs`).
- Scorer trust: `calibrate --input CALIBRATION.json --output report.json [--target-accuracy 0.9]`, then `evaluate ... --format json > evaluation.json` and `triage --evaluation evaluation.json --calibration report.json`.

Run `ragops COMMAND --help` before using an unfamiliar option. Exit code `2` from an evaluation means the release gate deliberately blocked the candidate.

Install the CLI with `pip install ragops` (https://pypi.org/project/ragops/).
