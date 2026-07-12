# Decision log

| Date | Decision | Rationale | Status |
| --- | --- | --- | --- |
| 2026-07-12 | Build evaluation/release infrastructure, not another chatbot | Horizontal OSS and commercial potential | Accepted |
| 2026-07-12 | Keep the core local-first and dependency-free | Privacy, portability, and CI adoption | Accepted |
| 2026-07-12 | Use a Japanese troubleshooting scenario as reference evidence | Connect Japan/FDE narrative to a reusable product | Accepted |
| 2026-07-12 | Treat deterministic checks as the first layer | Explainability and repeatability before model judges | Accepted |
| 2026-07-12 | Keep reference retrieval/generation outside the core | Prevent product boundary drift | Accepted |
| 2026-07-12 | License repository HEAD and future releases under MIT | Lower adoption and contribution friction without weakening the OSS core | Accepted |
| 2026-07-12 | Repair trace 0.4 schema syntax without changing its fields or semantics | Restore the published schema as valid JSON before v1.5.0 | Accepted |
| 2026-07-12 | Keep the reusable pull-request gate as a read-only adapter | Make CI adoption easy without moving evaluation semantics or write permissions into GitHub Actions | Accepted |

Architecturally significant changes must be captured as ADRs; this table is
the concise presentation-oriented index.
