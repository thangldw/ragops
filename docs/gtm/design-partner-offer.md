# Design-partner offer

Use this page when inviting a team to run a RAGOps pilot. It is an invitation, not a claim: RAGOps has no production adoption evidence yet, and the demo is synthetic.

## What the team gets

- A release gate for one RAG or agent workflow, run offline on traces the team already records. No data leaves their environment.
- A `PASS`/`WARN`/`BLOCK` decision with the failed gates, affected cases and counterfactual remediation, in the CI formats they already use.
- Hands-on setup for the first scenario (about one working session).

## What we ask

- 2–4 weeks, one workflow, 3+ people using the gate on real releases.
- Consent to record the pseudonymous pilot observations below, and agreement on retention.
- An honest read-out, including when the gate was wrong or got in the way.

## How evidence is recorded

```bash
ragops pilot-init --output pilot --pilot-id acme-support --label "Acme support RAG"
```

This writes a blank manifest and observation file that `pilot-report` rejects until the partner approves and a human sets `consent_status` to `approved`. Then follow [production-pilot.md](production-pilot.md). Nothing is published without the partner approving the exact aggregate claims.

## Honest limits

Evaluator accuracy and known failures are in [evaluator-accuracy.md](../evaluator-accuracy.md). Lexical evaluators miss synonym paraphrases; semantic scores can be imported from Ragas, DeepEval or an LLM judge and calibrated against the team's own labels.
