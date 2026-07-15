# Demo and presentation kit

## Audience and decision

Use this kit with engineers or product/platform leaders deciding whether to
pilot RAGOps around an existing RAG or AI agent.

## Five-minute walkthrough

1. Ask: “After this prompt, retriever, embedding, dataset, or evaluator change,
   is the candidate still good enough to release?”
2. Run:

   ```bash
   pip install ragops==1.0.0
   ragops demo --output ragops-demo
   ```

3. Open `ragops-demo/release-report.html` and show the passing baseline and
   blocked candidate.
4. Trace one aggregate regression to its case, citation, metric delta, and
   policy rule.
5. Replace demo responses with the adopter's recorded responses or JSONL traces.

## Ten-minute presentation

Follow problem → product thesis → workflow → live evidence → architecture →
limitations → pilot recommendation. Use the two SVG infographics as static
fallbacks and keep vocabulary consistent: scenario, trace, evaluator, finding,
release gate, baseline, candidate, and decision.

## Portfolio summary

RAGOps is a dependency-free Python release gate with versioned scenarios,
portable traces, deterministic evaluators, baseline comparison, red-team
findings, CLI/API adapters, CI recipes, and reviewable JSON/Markdown/HTML
evidence. The reference deployment records a 25-point citation coverage and
precision regression for a lexical-only candidate.

## Claim boundary

The reference agent and benchmark are synthetic. They validate harness behavior
and architecture integration, not Japanese semantic quality, production
security, customer adoption, or ROI. The local control plane is not hosted SaaS.

## Short public copy

**RAGOps — regression release gates for RAG and AI agents.** Compare recorded
candidate behavior with an accepted baseline, apply versioned quality and
operational policy, and produce an explainable `PASS` or `BLOCK` locally.

Repository: <https://github.com/thangldw/ragops>

Showcase: <https://thangldw.github.io/ragops/>
