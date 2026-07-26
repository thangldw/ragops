# RAGOps architecture / Kiến trúc / アーキテクチャ

```mermaid
%%{init: {"theme":"base","themeVariables":{"background":"#FFFFFF","fontFamily":"Arial, sans-serif","lineColor":"#667085","primaryTextColor":"#172B4D"}}}%%
flowchart LR
    T["Portable traces<br/>Trace / トレース"]:::yellow
    S["Scenario & policy<br/>Kịch bản / 方針"]:::blue
    C["Dependency-free core<br/>Core offline"]:::purple
    E["Evidence bundle<br/>Bằng chứng / 証拠"]:::pink
    G{"PASS / WARN / FAIL"}:::green
    T --> C
    S --> C --> E --> G
    classDef yellow fill:#FFF4A3,stroke:#C9A227,stroke-width:2px,color:#172B4D
    classDef blue fill:#D9EAFD,stroke:#4C78A8,stroke-width:2px,color:#172B4D
    classDef purple fill:#E9DDF7,stroke:#8064A2,stroke-width:2px,color:#172B4D
    classDef pink fill:#FFE1E6,stroke:#C96A7B,stroke-width:2px,color:#172B4D
    classDef green fill:#DDF5E3,stroke:#4F9D69,stroke-width:2px,color:#172B4D
```

## English

`src/ragops/` owns portable evaluation semantics, deterministic comparison and statistical gates. `scenarios/` and `schemas/` are versioned contracts. `apps/` contains optional API and GitHub adapters. Reusable workflows are read-only callers of the same core and publish bounded evidence artifacts.

## Tiếng Việt

`src/ragops/` quản lý evaluation portable, so sánh xác định và statistical gate. `scenarios/` cùng `schemas/` là contract có version. `apps/` chứa adapter API/GitHub tùy chọn. Reusable workflow chỉ đọc, gọi cùng core và xuất evidence artifact có giới hạn.

## 日本語

`src/ragops/` がポータブル評価、決定的比較、統計ゲートを担当します。`scenarios/` と `schemas/` はバージョン管理された契約です。`apps/` は任意の API・GitHub アダプターです。再利用可能 workflow は同じコアを読み取り専用で呼び出し、上限付き証拠を出力します。
