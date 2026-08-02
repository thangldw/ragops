# RAGOps operations / Vận hành / 運用

## English

Install with `pip install -e '.[dev]'`, run `ruff check .`, then `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q`. A release candidate must also exercise representative `inspect`, `evaluate`, `compare` and statistical commands. Build and validate from a clean commit, create the full semantic-version tag, promote the exact artifacts to a GitHub Release, then dispatch the release-only PyPI Trusted Publishing workflow.

## Tiếng Việt

Cài bằng `pip install -e '.[dev]'`, chạy `ruff check .`, sau đó `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q`. Release candidate phải chạy thêm các lệnh `inspect`, `evaluate`, `compare` và statistical tiêu biểu. Build và kiểm tra từ commit sạch, tạo tag semantic version đầy đủ, đưa đúng artifact lên GitHub Release rồi chạy workflow Trusted Publishing dành riêng cho PyPI.

## 日本語

`pip install -e '.[dev]'` で導入し、`ruff check .`、`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q` を実行します。リリース候補では代表的な `inspect`、`evaluate`、`compare`、統計コマンドも確認します。クリーンな commit で build と検証を行い、完全な semantic-version tag と同一 artifact の GitHub Release を作成して、PyPI 専用 Trusted Publishing workflow を実行します。
