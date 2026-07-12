# Japanese troubleshooting reference agent

This reference application demonstrates the M2 RAGOps integration boundary. It
is an offline, deterministic GraphRAG-style workflow—not a claim that rules are
a replacement for an LLM.

## Customer scenario

A Japanese manufacturer wants field engineers to resolve incidents faster
without leaking restricted notes or allowing an agent to take external action
without approval. Answers must cite approved manuals and policies.

## Pipeline

```text
question + role
  -> ACL filter
  -> lexical retrieval + entity graph expansion
  -> authority/intent ranking
  -> answer / clarify / escalate / request approval
  -> portable trace 0.4
  -> RAGOps evaluation and release decision
```

## Run

```bash
PYTHONPATH=src:. python -m examples.japanese_troubleshooting_agent.cli \
  "A1000 E-42 の一次対応は？" --role engineer

PYTHONPATH=src:. python -m examples.japanese_troubleshooting_agent.cli \
  --suite examples/japanese_troubleshooting_agent/suite.json \
  --retriever graph \
  --output /tmp/graph-traces.jsonl

PYTHONPATH=src python -m ragops.cli evaluate \
  --scenario examples/japanese_troubleshooting_agent/scenario.json \
  --traces /tmp/graph-traces.jsonl \
  --evaluator citation_correctness \
  --evaluator claim_support
```

## Recorded experiment

The graph+ACL build passes all four reference cases. The lexical-only candidate
is blocked with a 25-point citation coverage/precision regression and a
21.88-point lexical-groundedness regression. See `results/comparison.md`.

## Boundaries

- Synthetic data only.
- Deterministic evidence composition, no model/provider credential.
- ACL enforcement is role-list simulation, not production identity.
- Graph expansion is a small explicit graph, not automatic knowledge-graph
  extraction.
- Business-impact metrics are rollout hypotheses, not observed outcomes.

