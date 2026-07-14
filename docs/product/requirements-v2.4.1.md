# Requirements v2.4.1 — documentation and visual-system refresh

## User story

As an engineer discovering RAGOps, I can read the project comfortably, follow
one current documentation path, and understand workflows from clear,
lightweight diagrams without downloading fonts or visual assets from third-party
services.

## Contract impact

This maintenance slice changes presentation, documentation navigation, and
static assets only. It is backwards compatible and does not change a public
schema, metric meaning, release-gate decision, CLI/API behavior, or the
open-core boundary.

## Acceptance criteria

- Every browser-facing surface uses a local system-font stack and makes no font
  request to an external service.
- The showcase is responsive, accessible, and uses a board-style visual system
  for workflow, evidence, and architecture content.
- SVG infographics and active Mermaid diagrams use the same light canvas,
  colored cards, and explicit connector vocabulary.
- Active Markdown has one discoverable index, current wording, working local
  links, and no superseded launch-status or handoff documents.
- Historical ADRs, released requirements, acceptance records, release notes,
  and their referenced evidence remain preserved as immutable records.
- Ruff, the full test suite, sample PASS/BLOCK paths, site structure checks,
  desktop/mobile visual QA, package build, and clean install are verified.

## Non-goals

- No hosted font, analytics, tracking, framework, or build-time web dependency.
- No claim that synthetic evidence proves semantic correctness, production
  security, customer adoption, or ROI.
- No publication, tag, package upload, or GitHub Pages deployment without
  explicit owner instruction.
