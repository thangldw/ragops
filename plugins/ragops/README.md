# RAGOps plugin for Claude Code and Cowork

Gate RAG and agent releases with evidence. The `evaluate-ai-release` skill drives the open-source
[RAGOps](https://github.com/thangldw/ragops) command-line tool: compare a candidate with an accepted baseline,
localize regressions, and get a verifiable PASS, WARN or BLOCK. It runs locally and needs no AI provider.

Requirements: Python 3.11+ and `pip install ragops` (see https://pypi.org/project/ragops/).

Install: `/plugin marketplace add thangldw/ragops`, then `/plugin install ragops@ragops`.

Limits: results are release evidence, not proof that a system is correct. Some checks (`counterfactual`) call
your own system through a command you provide; Claude states how many calls that means before running it.
Apache-2.0. Support: https://github.com/thangldw/ragops/blob/main/SUPPORT.md
