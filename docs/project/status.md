# Project status and acceptance

## Current state

- Stable package: `2.4.0`.
- Repository license: MIT.
- Runtime contract: unchanged by the documentation cleanup.
- Current work: simplify repository HEAD and make `main` the only Pages source.

## Compatibility

The cleanup changes documentation URLs and GitHub Pages operations only. Public
schemas, metric meaning, PASS/BLOCK behavior, Python/CLI/API contracts, and the
open-core boundary remain compatible.

## Release readiness

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

## Current limitations

- Synthetic fixtures validate harness behavior, not semantic quality, customer
  adoption, production security, or ROI.
- The reference ACL and graph are deterministic simulations.
- The control plane is a local development alpha, not hosted multi-tenant SaaS.
- Provider-backed evaluators own their reproducibility, privacy, calibration,
  and availability guarantees.

## Recommendation

Hold release, tag, and package publication until the owner reviews the final
diff and acceptance evidence. Documentation and Pages publication may proceed
only after the complete local verification lane passes.
