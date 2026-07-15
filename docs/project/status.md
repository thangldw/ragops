# Project status and acceptance

## Current state

- Stable package: `2.4.0`.
- Repository license: MIT.
- Released runtime contract: `2.4.0` remains unchanged.
- Current work: prepare the opt-in statistical regression milestone for owner
  acceptance; all changes remain under `Unreleased`.

## Compatibility

Existing evaluation schemas, metric meanings, and deterministic PASS/BLOCK
behavior remain compatible. New replay, statistical, sequential, drift,
provenance, and baseline-manifest contracts are opt-in and pending owner
acceptance. The open-core boundary remains unchanged.

## Release readiness

### Current implementation evidence

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

This is implementation evidence, not an owner acceptance or release approval.
The release-only publication and browser-render lane remains intentionally
deferred until a large milestone is approved.

Before owner acceptance:

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

Hold release, tag, and package publication until the owner reviews the final
diff and acceptance evidence. Documentation and Pages publication may proceed
only after the complete local verification lane passes.
