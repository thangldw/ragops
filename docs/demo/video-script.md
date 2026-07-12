# Five-minute showcase video script

## 0:00–0:35 — Problem

Open the case-study hero. Explain that the customer request is ambiguous and
the production decision—not a chatbot—is the deliverable.

## 0:35–1:20 — Discovery and scope

Show the four constraints: trusted citations, ACL, controlled agency, and
measurable rollout. State the MVP boundary and success criteria.

## 1:20–2:15 — Reference system

Walk through question/role → ACL → lexical+graph retrieval → workflow decision
→ trace. Ask the Japanese A1000/E-42 question and show citations.

## 2:15–3:25 — Evaluation

Generate graph and lexical-only traces. Run `ragops compare`. Explain the 25
point citation regression and why the candidate is blocked.

## 3:25–4:20 — Safety and rollout

Show the executive-only document exclusion and email `request_approval`
decision. Present offline, shadow, 20-user pilot, and controlled scale phases.

## 4:20–5:00 — Honest decision

Recommend customer-reviewed offline pilot, not production. Close with the FDE
loop: discover, build, evaluate, deploy, measure, improve.

