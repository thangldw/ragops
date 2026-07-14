# Product roadmap

## Current slice — v2.4.1 owner review

The owner resumed a bounded maintenance slice on 2026-07-14. The objective is
to simplify active documentation, remove superseded presentation assets, adopt
a lightweight local typography system, and refresh the GitHub Pages showcase.

This slice is presentation-only. It does not change schemas, metric meaning,
release-gate behavior, CLI/API contracts, or the open-core boundary. See
[requirements v2.4.1](requirements-v2.4.1.md).

## Stable product

Release `2.4.0` remains the current published package. It provides:

- A dependency-free offline evaluation core.
- Versioned scenarios, response fixtures, traces, reports, and policies.
- Deterministic quality, safety, budget, and regression gates.
- Python and CLI surfaces plus optional API, browser, and provider adapters.
- Portable external evaluator metrics and pull-request release-gate recipes.
- Three credential-free demos and a synthetic reference deployment.
- Local release verification with checksums, SBOM, and clean-install evidence.

The detailed evolution of these capabilities belongs in immutable
[release notes](../releases/) and [acceptance records](../project/), not in this
active roadmap.

## Next decisions

After the v2.4.1 presentation slice is accepted, further implementation requires
a concrete user need and a new owner-approved requirement. Useful discovery
questions include:

- Which real workflow should become a reviewed regression fixture?
- Which evaluator meaning is stable enough to gate a release?
- Which CI or review surface creates the most adoption friction?
- Which production controls are required before processing customer evidence?

## Deferred hypothesis — hosted control plane

Hosted collaboration is not active roadmap work. It would require evidence of
customer demand plus separate decisions for identity, tenant isolation, legal,
security, retention, operations, and commercial boundaries. The existing local
alpha is not production multi-tenant infrastructure.
