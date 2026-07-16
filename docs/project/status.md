# Project status and acceptance

## Current state

- Stable package: `1.1.0`.
- Public GitHub milestone: `v1.1`.
- Repository license: MIT.
- Released runtime contract: `1.1.0`.
- Current work: the three-minute adoption milestone was accepted and published
  as the `v1.1` GitHub Release and `1.1.0` Python package on 2026-07-16.

## Compatibility

Existing evaluation schemas, metric meanings, and deterministic PASS/BLOCK
behavior remain compatible. New replay, statistical, sequential, drift,
provenance, and baseline-manifest contracts remain compatible. Source-freshness
and abstention-contract evaluation are opt-in additions in 1.1.0. The open-core
boundary remains unchanged.

## Released baseline

### v1.1 acceptance evidence

The 2026-07-16 acceptance lane completed on local and GitHub-hosted runners:

- `ruff check .` and 208 tests passed with third-party pytest plugin autoload
  disabled; CI passed on Python 3.11, 3.12, and 3.13.
- A clean, credential-free `uvx ragops demo` run from outside the repository
  installed `1.1.0`, produced a BLOCK decision, and wrote Markdown and HTML
  reports.
- The repository's reusable gate blocked the intentional regression and then
  passed the restored candidate. The same pull-request comment reported metric
  deltas, named block reasons, and the HTML artifact link.
- Wheel and source archive builds, clean-wheel execution, deterministic and
  statistical PASS/BLOCK paths, sequential decisions, evaluator drift,
  baseline integrity/signature verification, API authentication/body bounds,
  secret review, and desktop/mobile visual checks passed.
- The release workflow produced checksums, a reproducible CycloneDX SBOM, and
  build provenance. PyPI Trusted Publishing promoted the exact GitHub Release
  distributions without rebuilding.
- GitHub Pages deployed the merge commit and exposes the one-command demo,
  result screenshots, honest comparison, Failure Zoo, and concise roadmap.

The owner accepted this evidence and authorized release `v1.1` and package
`1.1.0` on 2026-07-16.

### v1.0 acceptance evidence

The 2026-07-15 pre-acceptance lane completed on Python 3.12:

- `ruff check .` and 202 tests passed with third-party pytest plugin autoload
  disabled.
- Wheel and source archive builds succeeded. A clean wheel install passed
  `pip check`, exposed every new CLI command, and reproduced the offline demo.
- Deterministic and fixed statistical fixtures reproduced PASS and BLOCK exit
  behavior; the sequential fixture stopped with PASS at its first eligible
  predeclared look.
- Frozen-anchor evaluator drift passed within tolerance, and baseline
  integrity plus a real detached Ed25519 SSH signature verified successfully.
- API health returned the package version, missing credentials returned 401,
  and an authenticated statistical comparison passed.
- Serialized contract fixtures and reports were validated against every new
  JSON Schema by the test suite. `git diff --check`, package-content review,
  and the repository secret-pattern scan passed.
- The showcase rendered at 1440px desktop and 390px mobile widths with the
  1.0.0 command, complete local images, no horizontal overflow, and no browser
  console warnings or errors.

The owner accepted this evidence and authorized the 1.0.0 milestone release on
2026-07-15. The verified pipeline published tag and GitHub Release `v1.0`, the
checksummed wheel and source archive, SBOM and release evidence, and Python
package `1.0.0` through PyPI Trusted Publishing. GitHub Pages reflects the
released statistical workflow and keeps the package command at `1.0.0`.

Acceptance checklist for the next milestone:

1. Run `ruff check .` and the full test suite.
2. Reproduce a passing baseline and blocked regression.
3. Check API health and authenticated evaluation.
4. Validate every schema, Markdown link, and visual asset.
5. Build wheel and source archive; clean-install the wheel and run the demo.
6. Review supported Python versions, dependencies, secrets, generated files,
   and repository status.
7. Render desktop and 390px mobile Pages views with no overflow or console
   errors.
8. Reproduce fixed PASS/BLOCK, sequential early PASS/BLOCK, evaluator drift,
   baseline integrity/signature verification, and bounded API requests.

## Current limitations

- Synthetic fixtures validate harness behavior, not semantic quality, customer
  adoption, production security, or ROI.
- The reference ACL and graph are deterministic simulations.
- The control plane is a local development alpha, not hosted multi-tenant SaaS.
- Provider-backed evaluators own their reproducibility, privacy, calibration,
  and availability guarantees.
- Generic bootstrap and provenance diagnostics do not replace domain-specific
  power analysis, labeled calibration, or controlled causal experiments.

## Recommendation

The current public baseline is GitHub milestone `v1.1` and Python package
`1.1.0`. Keep subsequent compatible work under `Unreleased`; publish another
version only after a new owner-approved acceptance lane.
