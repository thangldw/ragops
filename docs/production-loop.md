# Production loop / Vòng lặp production / 本番運用ループ

[English](#english) · [Tiếng Việt](#tiếng-việt) · [日本語](#日本語)

Five commands that connect real usage to the release gate: set a policy from a baseline, trust the
scorer only where it is accurate, catch unstable answers, grow the test set from production
failures, and test whether answers depend on their evidence. Every command is offline, makes no
network calls and needs no model provider (`counterfactual` calls only the command you give it).

```mermaid
%%{init: {"theme":"base","themeVariables":{"background":"#FFFFFF","fontFamily":"Arial, sans-serif","lineColor":"#667085","primaryTextColor":"#172B4D"}}}%%
flowchart LR
    B["Accepted baseline"]:::blue --> P["policy-suggest"]:::green
    P --> G{"gate-v2"}:::pink
    L["Production logs"]:::yellow --> M["mine"]:::purple --> S["Scenario grows"]:::blue
    S --> G
    H["Human labels"]:::yellow --> C["calibrate"]:::purple --> T["triage"]:::green
    R["Repeated runs"]:::yellow --> ST["stability"]:::purple --> G
    S --> CF["counterfactual"]:::purple --> G
    classDef yellow fill:#FFF4A3,stroke:#C9A227,stroke-width:2px,color:#172B4D
    classDef blue fill:#D9EAFD,stroke:#4C78A8,stroke-width:2px,color:#172B4D
    classDef purple fill:#E9DDF7,stroke:#8064A2,stroke-width:2px,color:#172B4D
    classDef pink fill:#FFE1E6,stroke:#C96A7B,stroke-width:2px,color:#172B4D
    classDef green fill:#DDF5E3,stroke:#4F9D69,stroke-width:2px,color:#172B4D
```

## English

### What was measured, and what was not

These tools were exercised on toy systems and on data constructed for the tests and demos. None has
been measured on a real production RAG system. Treat their output as a way to look at your own data
more carefully, not as a certificate. Where a section says "limits", read it.

### `policy-suggest`: a first policy from an accepted baseline

```bash
ragops policy-suggest --scenario scenario.json --baseline responses.json --output policy.toml
```

Writes a release policy v2 (TOML) with one slice per language, category and severity value that has
at least `--min-cases` cases (default 3) and does not cover the whole scenario. Each quality minimum
is the lowest baseline value among the whole set and the included slices, minus `--margin`
(default 0.05). So the baseline passes its own policy and a drop of more than the margin is blocked.
Review the file before use, then apply it with `ragops gate-v2`.

Limits: thresholds come from one baseline; they say "no worse than the accepted state", not "good".

### `calibrate` and `triage`: trust the scorer only where it agrees with people

```bash
ragops calibrate --input calibration.json --target-accuracy 0.9 --output calibration-report.json
ragops evaluate ... --format json > eval.json
ragops triage --evaluation eval.json --calibration calibration-report.json
```

`calibrate` compares automated scores with your human labels. It reports agreement, a
`suggested_threshold` (the pass threshold with the best accuracy among those within the false-pass
limit; ties go to the one closest to the current threshold) and a `confidence_band`: the narrowest
margin around the threshold outside of which the scorer agrees with your labels at
`--target-accuracy` (default 0.9, at least `--minimum-decided` cases, default 5). Exit code 0 on
`PASS`, 2 otherwise.

`triage` then sorts each case of an evaluation (`--metric`, default `lexical_groundedness`) into
`auto-pass`, `auto-fail` or `needs-review`: a score closer to the threshold than the margin goes to a
person; the rest are decided automatically and the report states the measured agreement on that
part. Exit code 0.

Limits: the band is only as good as the number and the spread of your labels; with few labels it can
be wide or absent, and then everything needs review.

### `stability`: the same question, answered differently each time

```bash
ragops collect-runs ...            # repeats each case and writes a replay bundle
ragops stability --bundle runs.json --baseline-bundle old-runs.json --max-stddev-increase 0.05
```

A case is unstable when a metric varies by more than `--max-range` (default 0.2) between repeats.
At most `--max-unstable-fraction` (default 0.1) of cases may be unstable. With `--baseline-bundle` and
`--max-stddev-increase`, a candidate whose mean per-case standard deviation grew by more than that
is blocked even if its average score did not move. `--metric` (repeatable) limits the metrics;
`--format json|markdown`. Exit code 0 on pass, 2 on `BLOCK`.

Limits: needs several repeats per case; a model that is deterministic at your settings always
passes.

### `mine`: grow the scenario from production failures

```bash
ragops mine --from logs.jsonl --scenario scenario.json --responses responses.json --output next/
```

Reads a JSON/JSONL file or a directory of logs and appends every flagged record (thumbs down,
rating at or below `--max-rating` (default 2), escalated, flagged, needs review) to the scenario as a
high-severity `mined-feedback` case. The failing answer is kept as that case's baseline response, so
a fixed system should beat it and the case guards against the failure returning. Questions already
in the scenario are skipped and the command refuses to overwrite existing output. It writes
`scenario.json`, `responses.json` and `mined.json` into `--output` and prints what was added or
skipped.

Limits: logs must contain the question, the answer and the evidence or citations; a flagged record
without them is reported as unusable. A thumbs-down is a signal, not proof the answer was wrong.

### `counterfactual` and `counterfactual-selftest`: do answers depend on the evidence?

```bash
ragops counterfactual --scenario s.json --responses r.json --answer-command "python my_app.py"
ragops counterfactual-selftest --scenario s.json --responses r.json
```

`counterfactual` changes the evidence (removes the supporting passages, swaps numbers, drops one
citation, plants an instruction, removes all evidence) and asks your own system again; it blocks when
too many answers ignore the change. `counterfactual-selftest` checks these checks on your own
scenario first: an evidence-copying reference should be left alone and an evidence-ignoring or
instruction-obeying system should be caught. Exit codes: counterfactual 0 PASS / 2 BLOCK /
3 INCONCLUSIVE; self-test 0 VALID / 2 WEAK / 3 INCONCLUSIVE. Full description, options and limits:
[counterfactual-test.md](counterfactual-test.md).

### How they fit together

1. Accept a baseline; `policy-suggest` drafts the policy; review it.
2. `calibrate` against a sample of human labels; `triage` the evaluations so people review only the
   uncertain cases.
3. In CI, run `gate-v2` and `stability`; run `counterfactual` when answers must be grounded.
4. After each incident, `mine` the flagged logs into the scenario so it cannot recur silently.

## Tiếng Việt

Năm lệnh nối việc dùng thật với cổng phát hành. Tất cả chạy offline, không gọi mạng, không cần
model provider (`counterfactual` chỉ gọi đúng lệnh bạn đưa).

**Giới hạn quan trọng:** các công cụ này mới được thử trên hệ thống mẫu và dữ liệu dựng sẵn cho test
và demo, chưa đo trên hệ RAG production thật. Hãy coi kết quả là cách xem dữ liệu của bạn kỹ hơn,
không phải chứng nhận.

- **`policy-suggest`**: sinh release policy v2 từ baseline đã chấp nhận. Mỗi ngưỡng chất lượng là giá
  trị baseline thấp nhất trừ `--margin` (mặc định 0,05), nên baseline qua được chính policy của nó.
  Hãy review trước khi dùng rồi áp dụng bằng `ragops gate-v2`.
- **`calibrate` + `triage`**: `calibrate` so điểm tự động với nhãn của người, đưa ra
  `suggested_threshold` và `confidence_band` (vùng quanh ngưỡng nơi scorer đủ tin cậy theo
  `--target-accuracy`, mặc định 0,9). `triage` chia từng case thành `auto-pass`, `auto-fail` hoặc
  `needs-review`; chỉ case gần ngưỡng mới cần người xem. Ít nhãn thì vùng tin cậy rộng hoặc không có,
  khi đó mọi case đều cần review.
- **`stability`**: chặn ứng viên trả lời không ổn định giữa các lần chạy (một case không ổn định khi
  metric lệch quá `--max-range`, mặc định 0,2; tối đa `--max-unstable-fraction`, mặc định 10%, case
  được phép không ổn định). Mã thoát 2 khi BLOCK.
- **`mine`**: thêm mọi log bị đánh dấu (thumbs down, rating ≤ `--max-rating`, escalated…) vào scenario
  thành case `mined-feedback` mức high; câu trả lời lỗi được giữ làm baseline của case đó. Bỏ qua
  câu hỏi đã có và không ghi đè output.
- **`counterfactual` / `counterfactual-selftest`**: đổi bằng chứng rồi hỏi lại hệ thống của bạn để xem
  câu trả lời có thật sự dựa vào bằng chứng; selftest kiểm tra chính các phép thử trên scenario của
  bạn trước. Chi tiết: [counterfactual-test.md](counterfactual-test.md).

Quy trình gợi ý: chấp nhận baseline → `policy-suggest` → `calibrate`/`triage` → CI chạy `gate-v2`,
`stability`, `counterfactual` → sau mỗi sự cố, `mine` log bị đánh dấu vào scenario.

## 日本語

本番利用とリリースゲートをつなぐ5つのコマンドです。すべてオフラインで動作し、ネットワーク通信や
モデルプロバイダーは不要です（`counterfactual` は指定したコマンドだけを呼び出します）。

**重要な制限:** これらはテスト・デモ用に作った玩具システムと構成データで確認したもので、実際の
本番 RAG では未測定です。結果は証明ではなく、自分のデータをより丁寧に見るための手段として扱って
ください。

- **`policy-suggest`**: 承認済みベースラインからリリース方針 v2 を生成します。各品質下限は
  ベースラインの最低値から `--margin`（既定 0.05）を引いた値で、ベースライン自身は合格します。
  使用前に確認し、`ragops gate-v2` で適用します。
- **`calibrate` + `triage`**: `calibrate` は自動スコアを人のラベルと比較し、`suggested_threshold` と
  `confidence_band`（`--target-accuracy`、既定 0.9 を満たす、しきい値周辺の外側の範囲）を出します。
  `triage` は各ケースを `auto-pass` / `auto-fail` / `needs-review` に分け、しきい値に近いものだけを
  人が確認します。ラベルが少ないと範囲は広くなり、全件が要確認になります。
- **`stability`**: 繰り返し実行で回答がぶれる候補をブロックします（指標が `--max-range`、既定 0.2
  を超えて変動したケースは不安定。不安定ケースは `--max-unstable-fraction`、既定 10% まで）。
  BLOCK の終了コードは 2。
- **`mine`**: 本番ログで問題とされたもの（thumbs down、`--max-rating` 以下の評価、エスカレーション
  など）をシナリオに `mined-feedback`（高重要度）として追加し、失敗した回答をそのケースの基準回答と
  して保持します。既存の質問は除外し、出力は上書きしません。
- **`counterfactual` / `counterfactual-selftest`**: 根拠を変えて自分のシステムに再質問し、回答が根拠に
  依存しているかを確認します。selftest は先に自分のシナリオでこの検査自体を確認します。詳細:
  [counterfactual-test.md](counterfactual-test.md)。

推奨手順: ベースライン承認 → `policy-suggest` → `calibrate`/`triage` → CI で `gate-v2`・`stability`・
`counterfactual` → 障害のたびにフラグ付きログを `mine` でシナリオへ。
