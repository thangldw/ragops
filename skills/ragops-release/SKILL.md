# RAGOps release validation

Use this skill to prepare a version for owner acceptance. It does not authorize
publishing, tagging, pushing, or releasing.

1. Read the release plan, changelog, acceptance record, and affected ADRs.
2. Verify clean installation and supported Python versions where available.
3. Run lint, tests, sample pass, sample regression, API health/evaluate, schema
   validation, and package build.
4. Check public version consistency across package, API, schemas, reports, and
   changelog.
5. Review security-sensitive changes, dependency changes, generated artifacts,
   and repository secrets.
6. Produce an acceptance report: passed evidence, failed evidence, limitations,
   compatibility impact, and an explicit go/hold recommendation.

Only the product owner accepts and publishes a release.

