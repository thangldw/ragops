# Current product requirement

## User story

As an engineer evaluating or maintaining RAGOps, I can find one current source
for product intent, architecture, integration, evaluation, and release guidance
without navigating obsolete milestone snapshots.

## Contract impact

This cleanup changes documentation paths, presentation assets, and GitHub Pages
operations. It does not change public schemas, metric meaning, release-gate
semantics, CLI/API behavior, package dependencies, or the open-core boundary.

The owner explicitly supersedes the v2.4.1 requirement to retain every
historical Markdown record in repository HEAD. Git history and the changelog are
the archive; HEAD contains current guidance only.

## Acceptance criteria

- Root README leads to install → evaluate → compare → release decision.
- One documentation index links every supported workflow.
- Product, architecture, engineering, evaluation, pilot, demo, and project
  status each have one canonical document.
- Superseded requirements, release snapshots, acceptance records, design
  audits, and duplicate guides are removed from HEAD.
- Every remaining local Markdown link resolves.
- Mermaid and SVG workflows use the same light canvas, colored cards, explicit
  connectors, and local system-font stack.
- GitHub Pages deploys `site/` from `main` through one enabled workflow; no
  deployment branch is required.
- Ruff, tests, PASS/BLOCK samples, API checks, package build, clean install, and
  desktop/mobile visual QA pass.

## Non-goals

- No release, tag, PyPI upload, metric recalibration, schema migration, or new
  hosted-service promise.
- No claim that lexical overlap proves semantic correctness.
- No claim that synthetic fixtures prove production security, adoption, or ROI.
