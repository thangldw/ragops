# RAGOps

[English](#english) · [Tiếng Việt](#tiếng-việt) · [日本語](#日本語)

Regression tests and explainable release gates for RAG systems and AI agents.

```mermaid
%%{init: {"theme":"base","themeVariables":{"background":"#FFFFFF","fontFamily":"Arial, sans-serif","lineColor":"#667085","primaryTextColor":"#172B4D"}}}%%
flowchart LR
    S["Scenario<br/>Kịch bản / シナリオ"]:::yellow
    B["Accepted baseline<br/>Mốc chuẩn / 基準"]:::blue
    C["Candidate traces<br/>Ứng viên / 候補"]:::purple
    E["Evaluators & policy<br/>Đánh giá / 評価"]:::green
    G{"PASS / WARN / FAIL"}:::pink
    S --> E
    B --> E
    C --> E --> G
    classDef yellow fill:#FFF4A3,stroke:#C9A227,stroke-width:2px,color:#172B4D
    classDef blue fill:#D9EAFD,stroke:#4C78A8,stroke-width:2px,color:#172B4D
    classDef purple fill:#E9DDF7,stroke:#8064A2,stroke-width:2px,color:#172B4D
    classDef green fill:#DDF5E3,stroke:#4F9D69,stroke-width:2px,color:#172B4D
    classDef pink fill:#FFE1E6,stroke:#C96A7B,stroke-width:2px,color:#172B4D
```

## English

RAGOps compares recorded candidate behavior with an accepted baseline, applies versioned release policy and returns explainable `PASS`, `WARN` or `FAIL` evidence. The dependency-free core works offline; optional adapters expose API and UI surfaces. Runtime integrations use the local CLI or API; the repository-owned GitHub Actions workflow is limited to PyPI publishing.

Requirements: Python 3.11+.

Current technical references: [architecture](docs/ARCHITECTURE.md), [operations](docs/OPERATIONS.md), [security](SECURITY.md) and [v1.2.0 release notes](docs/releases/v1.2.0.md).

The repository is also a skills-only plugin for ChatGPT, Codex, Claude Code and Cowork. It does not include a hosted MCP connector. See the [directory submission package](docs/submission/DIRECTORY_SUBMISSION.md), [privacy policy](PRIVACY.md), [terms](TERMS.md), and [support guidance](SUPPORT.md).

```bash
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/ragops inspect --scenario scenarios/japanese_troubleshooting/benchmark-v0.2.json
.venv/bin/ruff check .
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/pytest -q
```

## Tiếng Việt

RAGOps so sánh hành vi ứng viên đã ghi lại với baseline được chấp nhận, áp dụng policy phát hành có version và trả về bằng chứng giải thích được ở trạng thái `PASS`, `WARN` hoặc `FAIL`. Core không có dependency và chạy offline; adapter tùy chọn cung cấp API/UI. Tích hợp runtime dùng CLI hoặc API cục bộ; GitHub Actions thuộc repo chỉ dùng để phát hành PyPI.

Yêu cầu: Python 3.11+. Dùng các lệnh ở phần English để cài đặt, kiểm tra scenario, lint và test.

## 日本語

RAGOps は、記録済みの候補動作を承認済みベースラインと比較し、バージョン管理されたリリースポリシーを適用して、説明可能な `PASS`・`WARN`・`FAIL` の根拠を返します。依存関係のないコアはオフラインで動作し、任意のアダプターが API と UI を提供します。runtime integration はローカル CLI/API を使い、repository-owned GitHub Actions は PyPI 公開のみに使用します。

必要環境は Python 3.11 以上です。セットアップ、lint、テストには English セクションのコマンドを使用してください。

Released under the [MIT License](LICENSE).
