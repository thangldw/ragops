# RAGOps for Claude Code and Cowork

The `ragops` plugin gives Claude one skill, `evaluate-ai-release`, that runs the RAGOps CLI to gate a RAG or
agent release and explain the result. Everything runs locally: no account, API key or network access is needed
by default, and Python 3.11 or newer is the only requirement (the plugin bundles the dependency-free core).

## Install

```text
/plugin marketplace add thangldw/ragops
/plugin install ragops@ragops
```

On Claude Code 2.1.275 or later one step is enough: `/plugin install ragops --marketplace thangldw/ragops`.

## Use

Ask in plain language, for example:

- "Compare this candidate with the accepted baseline and explain the release decision."
- "Does the benchmark cover high-severity failure modes?"
- "Mine our thumbs-down logs into the scenario and re-run the gate."
- "Do these answers actually depend on the retrieved evidence?" (calls your system; Claude will say how many calls first)

The skill treats exit code 2 as an evaluated BLOCK, 3 (counterfactual) as INCONCLUSIVE, refuses to weaken
thresholds to obtain a pass, and never merges, tags or deploys on its own.

## What it does not do

- It is evidence for a release decision, not proof that a system is correct or safe. Grounding scores are
  lexical or claim-level; see the [RAGOps case studies](case-study-ragtruth.md) for measured limits.
- The bundled demo is synthetic. Nothing in the plugin implies production adoption.
- There is no hosted connector: the plugin runs the CLI on your machine.

## For maintainers

Skills for working on this repository live in `.claude/skills/` so they are not shipped to plugin users.
Before a release run `claude plugin validate . --strict` on a fresh checkout and keep `.claude-plugin/plugin.json`
in step with `pyproject.toml` (`python scripts/release_tools.py bump` does it).
