# RAGOps changelog / Lịch sử thay đổi / 変更履歴

## [Unreleased]

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

### English

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

### Tiếng Việt

- Thêm `ragops init --from LOGS` (kèm `--source-format langfuse|openai|anthropic`) và `ragops compare --format explorer` (báo cáo HTML tương tác). Nhiều loader từng crash với dữ liệu sai kiểu nay trả lỗi hợp đồng. Benchmark công khai (HaluEval, RAGTruth) cho thấy con số 93% của strict_grounding không khái quát hoá; chỉ nên dùng cho câu trả lời ngắn. Xem `docs/releases/v2.4.0.md`.
- Thêm evaluator plug-in `semantic_grounding` (`--semantic-command`): điểm theo từng claim từ scorer embedding/LLM của bạn, có chốt chặn lỗi số và đảo phủ định. Xem `docs/semantic-evaluator.md`.

### 日本語

- `ragops init --from LOGS`（`--source-format langfuse|openai|anthropic` 対応）と `ragops compare --format explorer`（インタラクティブ HTML レポート）を追加しました。型が不正な入力でクラッシュしていた複数のローダーが契約エラーを返すようになりました。公開ベンチマーク（HaluEval、RAGTruth）で strict_grounding の 93% は一般化しないことが分かり、短い回答にのみ推奨します。詳細は `docs/releases/v2.4.0.md`。
- プラグイン型 `semantic_grounding` evaluator（`--semantic-command`）を追加しました。独自の埋め込み/LLM スコアラーによる主張単位のスコアで、数値や否定の誤りを防ぎます。`docs/semantic-evaluator.md` を参照してください。

## [2.3.1] - 2026-11-19

### English

- `strict_grounding` now treats antonym pairs and mismatched proper nouns as contradictions, and no longer splits numbers such as `1,000`. Benchmark grew to 97 pairs; strict accuracy is 93% overall versus 72% for lexical groundedness.

### Tiếng Việt

- `strict_grounding` nay coi cặp từ trái nghĩa và danh từ riêng không khớp là mâu thuẫn, và không còn tách số như `1,000`. Benchmark tăng lên 97 cặp; strict đạt 93% so với 72% của lexical groundedness.

### 日本語

- `strict_grounding` は反意語の組と一致しない固有名詞を矛盾として扱い、`1,000` のような数値を分割しなくなりました。ベンチマークは 97 組になり、strict は全体で 93%（lexical groundedness は 72%）です。

## [2.2.1] - 2026-11-19

### English

- Same content as 2.2.0. PyPI refused the 2.2.0 filename (used by a since-deleted file), so 2.2.0 is a GitHub-only pre-release and 2.2.1 is the PyPI release.

### Tiếng Việt

- Nội dung giống 2.2.0. PyPI từ chối tên file 2.2.0 (từng được dùng bởi file đã xoá) nên 2.2.0 chỉ là pre-release trên GitHub, 2.2.1 là bản PyPI.

### 日本語

- 内容は 2.2.0 と同じです。2.2.0 のファイル名は PyPI に拒否されたため、2.2.0 は GitHub のみの pre-release、2.2.1 が PyPI release です。

## [2.2.0] - 2026-11-19

### English

- Added `ragops pilot-init`, which writes blank design-partner pilot files that `pilot-report` rejects until consent is recorded, and `docs/gtm/design-partner-offer.md`. This makes real evidence collection easier; it is not evidence.
- Added the opt-in `strict_grounding` evaluator (claim-level support, exact numbers/identifiers, negation contradictions) and a labeled grounding benchmark with `scripts/grounding_benchmark.py`; on the held-out split it scores 87% vs 71% for lexical groundedness. See `docs/evaluator-accuracy.md`.

### Tiếng Việt

- Thêm `ragops pilot-init` tạo file pilot trống mà `pilot-report` từ chối cho đến khi ghi nhận consent, và `docs/gtm/design-partner-offer.md`. Đây là công cụ thu thập bằng chứng thật, không phải bằng chứng.
- Thêm evaluator `strict_grounding` (tùy chọn): kiểm tra từng claim, khớp chính xác số/định danh, phát hiện mâu thuẫn phủ định; kèm bộ benchmark có nhãn. Trên tập heldout đạt 87% so với 71% của lexical groundedness. Xem `docs/evaluator-accuracy.md`.

### 日本語

- 同意が記録されるまで `pilot-report` が拒否する空のパイロットファイルを作る `ragops pilot-init` と `docs/gtm/design-partner-offer.md` を追加しました。実証データの収集を容易にするもので、実証そのものではありません。
- 任意の `strict_grounding` evaluator（主張単位の裏付け、数値・識別子の完全一致、否定の矛盾検出）とラベル付きベンチマークを追加しました。held-out で 87%（lexical groundedness は 71%）。`docs/evaluator-accuracy.md` を参照してください。

## [2.1.1] - 2026-11-19

### English

- Same content as 2.1.0. PyPI refused the 2.1.0 filename because it was used by a since-deleted file, so 2.1.0 exists only as a GitHub pre-release and 2.1.1 is the first PyPI release of these changes.

### Tiếng Việt

- Nội dung giống 2.1.0. PyPI từ chối tên file 2.1.0 vì từng được dùng bởi file đã xoá, nên 2.1.0 chỉ còn là pre-release trên GitHub và 2.1.1 là bản PyPI đầu tiên chứa các thay đổi này.

### 日本語

- 内容は 2.1.0 と同じです。2.1.0 のファイル名は削除済みファイルが使用していたため PyPI に拒否され、2.1.0 は GitHub の pre-release のみとなり、2.1.1 がこれらの変更を含む最初の PyPI release です。

## [2.1.0] - 2026-11-19

### English

- Moved the argument parser out of `cli.py` into `cli_parser.py` (`ragops.cli.build_parser` is unchanged).
- Added API HTTP, baseline-manifest, usage and Markdown-reporter tests and a CI coverage gate (`fail_under = 82`).
- Lexical groundedness now splits Japanese/Chinese runs into character bigrams and NFC-normalizes text; documented that it is a lexical baseline, not a semantic judge.
- Added a composite GitHub Action (`action.yml`) that applies a release policy v2 with `ragops gate-v2`, writes the canonical decision plus JUnit, SARIF and GitHub Summary renderings, and fails the step only when the decision is BLOCK. See `docs/examples/github-action-release-gate.yml`.

### Tiếng Việt

- Chuyển bộ phân tích tham số khỏi `cli.py` sang `cli_parser.py`; thêm test API/baseline/usage/reporter và ngưỡng coverage trong CI (`fail_under = 82`).
- Lexical groundedness tách chuỗi tiếng Nhật/Trung thành bigram ký tự và chuẩn hoá NFC; ghi rõ đây là baseline từ vựng, không phải bộ đánh giá ngữ nghĩa.
- Bổ sung GitHub Action dạng composite (`action.yml`) áp dụng release policy v2 bằng `ragops gate-v2`, ghi quyết định chuẩn cùng bản render JUnit, SARIF và GitHub Summary, và chỉ làm step thất bại khi quyết định là BLOCK. Xem `docs/examples/github-action-release-gate.yml`.

### 日本語

- 引数パーサーを `cli.py` から `cli_parser.py` に移動し、API・baseline・usage・reporter のテストと CI のカバレッジ基準 (`fail_under = 82`) を追加しました。
- lexical groundedness は日本語・中国語の連続文字を文字 bigram に分割し NFC 正規化します。意味的な評価器ではなく語彙ベースラインであることを明記しました。
- `ragops gate-v2` でリリースポリシー v2 を適用し、正規の判定と JUnit・SARIF・GitHub Summary を出力し、判定が BLOCK の場合のみステップを失敗させる composite GitHub Action (`action.yml`) を追加しました。`docs/examples/github-action-release-gate.yml` を参照してください。

## [2.0.2] - 2026-08-24

### English

- Added a deterministic synthetic retrieval-poisoning Failure Zoo specimen with explicit unsupported-citation, unsupported-claim, and forbidden-output findings.
- Added checkout-free Windows verification of the published package, least-privilege CodeQL scanning, and protected-branch release gates.
- Added disabled-by-default local usage evidence that records only command, exit code, version, and UTC timestamp without arguments or paths.
- Generate the CycloneDX SBOM from the built wheel in a dependency-free environment so its root version is exact and no local build path is disclosed.

### Tiếng Việt

- Bổ sung mẫu synthetic retrieval poisoning xác định với các finding rõ ràng về citation không được hỗ trợ, claim không có căn cứ và output bị cấm.
- Bổ sung kiểm tra Windows không checkout từ package đã public, CodeQL theo least privilege và release gate bảo vệ nhánh chính.
- Bổ sung bằng chứng sử dụng local mặc định tắt, chỉ ghi command, exit code, version và UTC timestamp, không ghi arguments hoặc paths.
- Tạo CycloneDX SBOM từ wheel đã build trong môi trường không dependency để version gốc chính xác và không lộ local build path.

### 日本語

- unsupported citation、unsupported claim、forbidden output を明示する決定的な synthetic retrieval-poisoning Failure Zoo specimen を追加しました。
- 公開 package の checkout-free Windows 検証、least-privilege CodeQL、保護 branch release gate を追加しました。
- デフォルト無効で、引数や path を記録せず command、exit code、version、UTC timestamp のみを残す local usage evidence を追加しました。
- build 済み wheel を dependency-free environment で読み取り、正確な root version と local build path を含まない CycloneDX SBOM を生成します。

## [2.0.1] - 2026-08-23

### English

- Republished the unchanged RAGOps 2.0 feature set under a new patch version because PyPI permanently reserves filenames from deleted releases.
- Corrected the Trusted Publishing action reference so GitHub Actions uses the published v1.14.2 container with Core Metadata 2.5 support.

### Tiếng Việt

- Phát hành lại toàn bộ tính năng RAGOps 2.0 dưới patch version mới vì PyPI khóa vĩnh viễn filename của release đã bị xóa.
- Sửa tham chiếu Trusted Publishing để GitHub Actions dùng container v1.14.2 đã phát hành và hỗ trợ Core Metadata 2.5.

### 日本語

- 削除済みリリースのファイル名を PyPI が恒久的に予約するため、RAGOps 2.0 の機能を新しいパッチ版で再公開しました。
- Trusted Publishing の参照を修正し、Core Metadata 2.5 対応の公開済み v1.14.2 コンテナを使用します。

## [2.0.0] - 2026-08-23

### English

- Added versioned contract migration, content-addressed evidence bundles, slice/distribution gates, evaluator calibration, trace-graph evaluation, dataset leakage controls, CI renderers, portable vendor adapters, and audited blind review.
- Packaged the optional FastAPI workbench with CSP-safe DOM rendering and added Python 3.11-3.13 CI.
- Upgraded the synthetic flagship demo to generate canonical JSON, Markdown, HTML, JUnit, SARIF, GitHub Summary, and verified evidence for executive, engineer, and auditor profiles.
- Added a deterministic ChatGPT skills-only plugin bundle and v2 release evidence.

### Tiếng Việt

- Bổ sung contract có version, evidence bundle content-addressed, slice/distribution gate, calibration, trace graph, chống dataset leakage, CI renderer, vendor adapter và blind review có audit.
- Đóng gói FastAPI workbench tùy chọn với CSP/DOM an toàn và CI Python 3.11-3.13.
- Nâng demo synthetic để xuất cùng một quyết định qua JSON, Markdown, HTML, JUnit, SARIF, GitHub Summary và evidence đã xác minh.

### 日本語

- versioned contract、content-addressed evidence、slice/distribution gate、calibration、trace graph、dataset leakage check、CI renderer、vendor adapter、blind review audit を追加しました。
- CSP-safe な任意 FastAPI workbench と Python 3.11-3.13 CI を同梱しました。
- synthetic flagship demo は同一判定を JSON、Markdown、HTML、JUnit、SARIF、GitHub Summary、検証済み evidence に出力します。

## [1.2.0] - 2026-08-02

### English

- Added skills-only plugin packages and directory metadata for ChatGPT, Codex, Claude Code, Cowork and Kimi Code.
- Added the credential-free customer-support release-gate demonstration and its recorded evidence.
- Restored a release-only GitHub Actions workflow for PyPI Trusted Publishing; runtime integrations remain local CLI/API workflows.

### Tiếng Việt

- Bổ sung package plugin dạng skills-only và metadata directory cho ChatGPT, Codex, Claude Code, Cowork và Kimi Code.
- Bổ sung demo release gate cho customer support không cần credential cùng bằng chứng đã ghi lại.
- Khôi phục GitHub Actions chỉ dùng để phát hành PyPI qua Trusted Publishing; tích hợp runtime vẫn chạy qua CLI/API cục bộ.

### 日本語

- ChatGPT、Codex、Claude Code、Cowork、Kimi Code 向けの skills-only plugin package と directory metadata を追加しました。
- 認証情報不要の customer-support release-gate demo と記録済み証拠を追加しました。
- PyPI Trusted Publishing 専用の GitHub Actions workflow を復元しました。runtime integration は引き続きローカル CLI/API を使用します。

## [1.0.0] - 2026-07-26

### English

- Consolidated deterministic and statistical evaluation, policy comparison, provenance diagnosis, offline evidence and API/CLI adapters into one stable baseline.
- Removed all repository-owned GitHub Actions; release gates remain available through the local CLI and API.
- Standardized the public tag and package version at `v1.0.0`.

### Tiếng Việt

- Hợp nhất đánh giá xác định/thống kê, so sánh policy, chẩn đoán provenance, bằng chứng offline và adapter API/CLI vào một baseline ổn định.
- Xóa toàn bộ GitHub Actions thuộc repo; release gate tiếp tục hoạt động qua CLI và API cục bộ.
- Chuẩn hóa tag public và package version thành `v1.0.0`.

### 日本語

- 決定的・統計的評価、ポリシー比較、来歴診断、オフライン証拠、API/CLI アダプターを1つの安定版へ統合しました。
- リポジトリ所有の GitHub Actions をすべて削除し、リリースゲートはローカル CLI と API で引き続き利用できます。
- 公開タグとパッケージ版を `v1.0.0` に統一しました。

[2.0.2]: https://github.com/thangldw/ragops/releases/tag/v2.0.2
[2.0.1]: https://github.com/thangldw/ragops/releases/tag/v2.0.1
[2.0.0]: https://github.com/thangldw/ragops/releases/tag/v2.0.0
[1.2.0]: https://github.com/thangldw/ragops/releases/tag/v1.2.0
[1.0.0]: https://github.com/thangldw/ragops/releases/tag/v1.0.0
