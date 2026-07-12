# OSS launch plan

## Launch contract

Do not optimize for stars before a new user can reach evidence quickly. Launch
only after the demo, documentation, release metadata, and contributor paths
agree with the current code.

## Repository changes completed

- Adoption-first showcase and 1280 × 640 social preview asset.
- Credential-free `ragops demo` path.
- MIT license for repository HEAD and future releases.
- Bug, feature, evaluator, and design-partner issue forms.
- Contributor, support, conduct, security, and roadmap guidance.

## GitHub settings checklist

The following settings are outside Git and must be applied by the repository
owner:

1. About description: `Release gates, red-team checks, and evidence reports for RAG and agent systems.`
2. Website: `https://thangldw.github.io/ragops/`
3. Topics: `rag`, `llm`, `llm-evaluation`, `ai-agents`, `red-teaming`,
   `evals`, `python`, `ci-cd`, `observability`, `graphrag`, `ai-safety`.
4. Social preview: upload `docs/demo/social-preview.png`.
5. Enable Discussions with Welcome, Q&A, and Show and Tell categories.
6. Protect `main`, require CI, disable force pushes, and enable available
   dependency, secret, and security alerts.
7. Create the PyPI `ragops` project and configure a Trusted Publisher before
   enabling release publication.

## Release readiness gaps

- GitHub's latest public release must be synchronized with package version and
  changelog before launch.
- PyPI publication is not active, so public instructions must not claim that
  `pip install ragops` works from the registry.
- Create real starter issues from the backlog and apply `good first issue`,
  `help wanted`, `documentation`, or `integration` labels as appropriate.

## Distribution loop

1. Publish a release with the demo bundle and concise release evidence.
2. Record a 60–90 second regression-to-BLOCK walkthrough.
3. Publish one technical article explaining why evaluation dashboards alone do
   not create release gates.
4. Share the same reproducible evidence through GitHub, LinkedIn, Hacker News,
   and focused Python/LLM communities with one call to action: run the demo.
5. Recruit five design partners using synthetic or redacted traces and convert
   validated friction into public adapters, evaluators, and case studies.

## Funnel metrics

Track showcase-to-GitHub clicks, demo completions, CI integrations, returning
repositories, external issues/PRs, and design-partner conversions. Stars are a
distribution signal, not the product outcome.
