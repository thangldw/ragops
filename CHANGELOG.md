# RAGOps changelog / Lịch sử thay đổi / 変更履歴

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
