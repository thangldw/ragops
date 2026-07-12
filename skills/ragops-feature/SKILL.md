# RAGOps feature implementation

Use this skill for a new or changed RAGOps capability.

1. Read `AGENTS.md`, the related product requirement, architecture overview,
   and relevant ADRs completely.
2. Write the user story, public contract impact, acceptance criteria, and
   explicit non-goals before editing code.
3. Keep evaluation semantics in `src/ragops/`; keep adapters in `apps/`.
4. Add contract, unit, integration, and negative tests proportional to risk.
5. Preserve offline deterministic behavior unless an optional plugin is the
   stated scope.
6. Run lint and the full test suite, then exercise the affected CLI/API path.
7. Update docs and changelog. Report limitations and owner decisions required.

Never silently change metric meaning, schema compatibility, critical-gate
behavior, or the open-core boundary.

