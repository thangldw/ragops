# RAGOps changelog

## [Unreleased]

## [2.7.1] - 2026-11-20

- The Codex/ChatGPT plugin manifest now declares `interface.supportURL` (the OpenAI plugin portal requires it), so the published ChatGPT package and the GitHub release are identical. No CLI changes.

## [2.7.0] - 2026-11-20

- New `ragops counterfactual-selftest`: lets users check the counterfactual checks on their own scenario without any system. It builds an evidence-copying reference and an evidence-ignoring (or injection-obeying) system from the user's cases and reports, per perturbation, how often the reference is wrongly flagged, how often the failing system is caught, and whether enough cases apply (`valid`, `weak`, `too_few_cases`; exit 0, 2, 3).

## [2.6.0] - 2026-11-20

- `ragops counterfactual` gains three opt-in perturbations (`--perturbation all`): `drop_citation` (each cited passage removed in turn; flags citations the answer did not use), `inject_instruction` (a planted canary instruction in the evidence; one obeyed injection blocks, `--max-injection-rate` default 0) and `abstain_without_evidence` (no evidence at all; the answer should be a refusal, with `--abstain-pattern` for custom phrases). The demo has a third toy system that obeys injected text.
- New `ragops counterfactual` (see `docs/counterfactual-test.md`): alters the evidence of each case (removes the supporting passages, swaps the numbers the answer took from it) and re-asks your own system through `--answer-command`; blocks when more than `--max-insensitive-rate` of eligible answers ignore the change, and reports INCONCLUSIVE (exit 3) when too few cases were eligible. Needs no labels or model. Demonstrated on two toy systems only; not yet measured on a real RAG system.
- Evaluators can now say "not sure". `ragops calibrate` reports a `confidence_band` (`--target-accuracy`, default 0.9; `--minimum-decided`, default 5): the narrowest margin around the threshold outside of which the evaluator agrees with your human labels at the target accuracy. New `ragops triage --evaluation eval.json --calibration report.json` sorts cases into auto-pass, auto-fail and needs-review, and states the measured agreement on the part it decides alone.
- New `ragops stability --bundle B [--baseline-bundle B0]`: reads a replay bundle from `collect-runs` and blocks when the same cases vary too much between repeats (a case is unstable when a metric's range exceeds `--max-range`; at most `--max-unstable-fraction` of cases may be unstable; `--max-stddev-increase` compares mean per-case stddev with a baseline). Catches a candidate that became less repeatable even when its average did not move. Exit code 2 on BLOCK.
- New `ragops mine --from LOGS --scenario S --responses R --output DIR`: appends production failures (thumbs down, rating at or below `--max-rating`, escalated, flagged) to an existing scenario as high-severity `mined-feedback` cases, skipping questions already present. The failing answer stays as the baseline response, so a fixed system should beat it and the case guards against the failure returning.
- Mutation testing now also covers the release policy engine (`policy_v2.py`). It found that inclusive/exclusive boundaries, the `lower` direction, regression budgets, tail gates, slice `minimum_cases` and waiver windows were not pinned by any test; `tests/test_policy_v2_gate_semantics.py` now does (2023 of 2340 mutants killed across the five modules, up from 659 of 1152 on first run).

## [2.5.0] - 2026-11-20

- Real mutation testing with `mutmut` (new `mutation` extra, config in `pyproject.toml`) on the calibration, explain, policy-suggest and CI-renderer modules. The first run killed 65% of 1152 mutants; new boundary, exact-value and malformed-input tests raised that to 91% (1041 of 1149). It also showed one redundant ranking key in `suggest_threshold`, now removed. Plain-language gate summaries now read "Overall, the …" / "For the ja slice, the …".
- Added `.github/workflows/weekly.yml`: every Monday (and on demand) it installs the newest dependency releases, runs the test suite and the grounding benchmark, and writes the benchmark numbers to the job summary, so upstream breakage or an accuracy regression surfaces without waiting for a pull request.
- New `ragops policy-suggest --scenario S --baseline R [--margin 0.05] [--min-cases 3]` writes a release policy v2 from an accepted baseline: one slice per language, category and severity value with enough cases, and quality minimums set from the lowest baseline value minus the margin, so the baseline passes its own policy and a larger drop is blocked. Review the output before use.
- `ragops explain` and the PR comment now start each failing gate with one plain sentence saying why it failed (for example "The citation coverage overall dropped by 0.5 compared with the baseline; the policy allows at most 0"). New `summary` field in the explanation JSON.
- `ragops calibrate` reports `suggested_threshold`: the pass threshold with the best accuracy against your human labels among those within the false-pass limit (ties go to the one closest to the current threshold), with its accuracy and false-pass/false-block rates. `meets_false_pass_limit` is false when no threshold can satisfy the limit.

## [2.4.0] - 2026-11-19

- `ragops init --candidate LOGS` takes logs of a later run, matches answers to baseline cases by id or question text and writes `candidate.json` plus a `compare-report.md`, so the first regression check needs no hand-written files.
- Added `scripts/ragtruth_span_check.py`: explorer highlights land on annotated RAGTruth hallucination spans about 2x more than chance (precision 5.5 to 11.5%, recall 31 to 41%) but also mark about 16% of clean text. Documented as a reading aid, not a detector.
- `scripts/nli_ragtruth_probe.py` can pick evidence by IDF overlap (`bm25`) and reports min and mean sentence aggregation. Neither improves off-the-shelf NLI on RAGTruth QA (AUROC 0.68 and 0.63 vs 0.76 for lexical); documented in `docs/semantic-evaluator.md`.
- Added `examples/nli_scorer.py`, an optional local entailment scorer for `semantic_grounding`, and `scripts/nli_ragtruth_probe.py`. Measured result: off-the-shelf NLI models (AUROC 0.62 to 0.68) did not beat lexical grounding (0.76) on RAGTruth QA, so semantic scoring is documented as something to calibrate, not assume.
- Coverage gate raised to 91% (measured 92.1%). New mutation tests over the pilot, dataset, evidence, trace-graph, replay-bundle and statistical-policy loaders found and fixed more crashes: wrongly typed values raised `TypeError`/`KeyError` instead of the loader's own contract error. A shared `contract_guard` converts them.
- Removed all remaining mypy `ignore_errors` overrides (`cli`, `pilot`, `sequential`, `statistical`, `policy_v2`): the whole package is now type-checked. Missing absolute thresholds now raise `ContractError` instead of a `TypeError`.
- Added `scripts/ragtruth_benchmark.py` and `docs/case-study-ragtruth.md`: on long RAG answers from the public RAGTruth set, `strict_grounding` is near chance (AUROC 0.53 to 0.58) and lexical groundedness is weak (0.68 to 0.76). Strict grounding is documented as suitable for short factual answers only.
- `strict_grounding` now treats number words as digits (`nine` = `9`) and flags a two-word name written in reversed order (`Brooks Garth` vs `Garth Brooks`) as a contradiction. On HaluEval this does not change accuracy (91.0%); see the error breakdown in `docs/case-study-halueval.md`.
- Added `scripts/public_benchmark.py` and `docs/case-study-halueval.md`: a zero-shot check on 10,000 public HaluEval QA pairs. Result: lexical 92.9%, strict 91.0%, so the 93% vs 72% advantage from the maintainer-labeled benchmark did not reproduce. Docs now say so.
- `ragops init --source-format langfuse|openai|anthropic` imports Langfuse trace exports and OpenAI/Anthropic request-response logs directly. Records without retrieved context are skipped, never guessed; cost is taken only when present.
- New `ragops init --from LOGS --output DIR`: infers a scenario from your own JSON/JSONL RAG logs, writes `scenario.json`, `responses.json` and a first `strict_grounding` report in about a second. See `docs/quickstart-init.md`.
- New `ragops compare --format explorer`: a single self-contained HTML report with category/language/severity/status filters, text search, side-by-side baseline vs candidate answers, per-case metrics and highlighting of answer words that have no counterpart in the evidence (lexical visual aid, not a verdict). No network access; a Content-Security-Policy allows only its own script by hash.
- Added property-based and tamper tests (Hypothesis) for the scenario, response, trace-graph, OpenTelemetry, contract and evidence loaders. They found and fixed crashes: wrongly typed JSON values raised `TypeError`/`AttributeError`, and a non-UTF-8 evidence/dataset/contract/decision file raised `UnicodeDecodeError`, instead of a `ContractError`.
- Moved CLI helper functions into `cli_helpers.py` (`cli.py` is now ~770 lines).
- Coverage gate raised to 88% (now ~88.1%) with in-process CLI tests and mutation tests for policy and run-plan loaders. Fixed: a release policy v2 with a wrongly typed value (for example `insufficient_evidence = []`) raised `TypeError` instead of a `ContractError`; an OpenTelemetry export containing a non-object span raised `AttributeError` instead of a `ContractError`.
- CI now runs Python 3.11–3.15 on Linux plus 3.12 on macOS and type-checks with mypy (existing debt is listed in `pyproject.toml`; new modules are checked).
- Added `scripts/release_tools.py` (`bump` edits every version-bearing file; `check` rejects burned, already-published and non-increasing versions) and made version assertions in tests derive from `pyproject.toml`.
- The GitHub Action gains `comment: true`: one sticky pull-request comment with the decision, what to change (observed vs threshold, affected cases) and the full gate table; skipped on forks. `ragops ci-render --format comment` renders the same text.
- Added `scripts/grounding_labels.py` for blind relabeling of the grounding benchmark: export a label sheet, ingest reviewer sheets, report kappa and disagreements, and build a calibration set for `ragops calibrate`.
- Added the pluggable `semantic_grounding` evaluator (`--semantic-command`): per-claim scores from your own embedding/LLM scorer, guarded against wrong numbers and polarity flips. See `docs/semantic-evaluator.md`.

## [2.3.1] - 2026-11-19

- `strict_grounding` now treats antonym pairs and mismatched proper nouns as contradictions, and no longer splits numbers such as `1,000`. Benchmark grew to 97 pairs; strict accuracy is 93% overall versus 72% for lexical groundedness.

## [2.2.1] - 2026-11-19

- Same content as 2.2.0. PyPI refused the 2.2.0 filename (used by a since-deleted file), so 2.2.0 is a GitHub-only pre-release and 2.2.1 is the PyPI release.

## [2.2.0] - 2026-11-19

- Added `ragops pilot-init`, which writes blank design-partner pilot files that `pilot-report` rejects until consent is recorded, and `docs/gtm/design-partner-offer.md`. This makes real evidence collection easier; it is not evidence.
- Added the opt-in `strict_grounding` evaluator (claim-level support, exact numbers/identifiers, negation contradictions) and a labeled grounding benchmark with `scripts/grounding_benchmark.py`; on the held-out split it scores 87% vs 71% for lexical groundedness. See `docs/evaluator-accuracy.md`.

## [2.1.1] - 2026-11-19

- Same content as 2.1.0. PyPI refused the 2.1.0 filename because it was used by a since-deleted file, so 2.1.0 exists only as a GitHub pre-release and 2.1.1 is the first PyPI release of these changes.

## [2.1.0] - 2026-11-19

- Moved the argument parser out of `cli.py` into `cli_parser.py` (`ragops.cli.build_parser` is unchanged).
- Added API HTTP, baseline-manifest, usage and Markdown-reporter tests and a CI coverage gate (`fail_under = 82`).
- Lexical groundedness now splits Japanese/Chinese runs into character bigrams and NFC-normalizes text; documented that it is a lexical baseline, not a semantic judge.
- Added a composite GitHub Action (`action.yml`) that applies a release policy v2 with `ragops gate-v2`, writes the canonical decision plus JUnit, SARIF and GitHub Summary renderings, and fails the step only when the decision is BLOCK. See `docs/examples/github-action-release-gate.yml`.

## [2.0.2] - 2026-08-24

- Added a deterministic synthetic retrieval-poisoning Failure Zoo specimen with explicit unsupported-citation, unsupported-claim, and forbidden-output findings.
- Added checkout-free Windows verification of the published package, least-privilege CodeQL scanning, and protected-branch release gates.
- Added disabled-by-default local usage evidence that records only command, exit code, version, and UTC timestamp without arguments or paths.
- Generate the CycloneDX SBOM from the built wheel in a dependency-free environment so its root version is exact and no local build path is disclosed.

## [2.0.1] - 2026-08-23

- Republished the unchanged RAGOps 2.0 feature set under a new patch version because PyPI permanently reserves filenames from deleted releases.
- Corrected the Trusted Publishing action reference so GitHub Actions uses the published v1.14.2 container with Core Metadata 2.5 support.

## [2.0.0] - 2026-08-23

- Added versioned contract migration, content-addressed evidence bundles, slice/distribution gates, evaluator calibration, trace-graph evaluation, dataset leakage controls, CI renderers, portable vendor adapters, and audited blind review.
- Packaged the optional FastAPI workbench with CSP-safe DOM rendering and added Python 3.11-3.13 CI.
- Upgraded the synthetic flagship demo to generate canonical JSON, Markdown, HTML, JUnit, SARIF, GitHub Summary, and verified evidence for executive, engineer, and auditor profiles.
- Added a deterministic ChatGPT skills-only plugin bundle and v2 release evidence.

## [1.2.0] - 2026-08-02

- Added skills-only plugin packages and directory metadata for ChatGPT, Codex, Claude Code, Cowork and Kimi Code.
- Added the credential-free customer-support release-gate demonstration and its recorded evidence.
- Restored a release-only GitHub Actions workflow for PyPI Trusted Publishing; runtime integrations remain local CLI/API workflows.

## [1.0.0] - 2026-07-26

- Consolidated deterministic and statistical evaluation, policy comparison, provenance diagnosis, offline evidence and API/CLI adapters into one stable baseline.
- Removed all repository-owned GitHub Actions; release gates remain available through the local CLI and API.
- Standardized the public tag and package version at `v1.0.0`.

[2.0.2]: https://github.com/thangldw/ragops/releases/tag/v2.0.2
[2.0.1]: https://github.com/thangldw/ragops/releases/tag/v2.0.1
[2.0.0]: https://github.com/thangldw/ragops/releases/tag/v2.0.0
[1.2.0]: https://github.com/thangldw/ragops/releases/tag/v1.2.0
[1.0.0]: https://github.com/thangldw/ragops/releases/tag/v1.0.0
