# M2 executive decision report

## Recommendation

**Proceed to a customer-reviewed offline pilot; do not deploy to production.**

## Evidence

- The graph+ACL reference build passes four end-to-end scenario cases.
- Citation coverage, citation precision, lexical groundedness, claim support,
  and citation correctness are 1.0 on the synthetic suite.
- The lexical-only candidate is correctly blocked by RAGOps.
- Engineer-role retrieval excludes the synthetic executive-only document.
- External email requests return an approval decision instead of execution.

## What this proves

The application-to-trace-to-release-gate integration works, and retrieval
architecture changes can produce reviewable regressions.

## What this does not prove

It does not prove semantic model quality, production ACL correctness, user
adoption, or business ROI. Those require customer-reviewed data, identity
integration, shadow-mode observation, and a measured pilot.

