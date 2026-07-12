# Red-team plan

## Attack packs

- Direct and indirect prompt injection.
- Secret and personal-data extraction.
- Cross-role and cross-project permission leakage.
- Retrieval poisoning and malicious citation.
- Tool argument manipulation and excessive agency.
- Obfuscated output using encoding or spacing.
- Multi-turn instruction persistence.

## Attack-pack contract direction

An attack case needs an ID, category, input or trace mutation, expected policy,
severity, and pass condition. Deterministic detectors run first; model-based
attack generation and judging are optional plugins.

## Reporting

Report attack coverage by category and severity. A zero finding count must not
be described as “secure” when the suite lacks relevant attacks.

## Safety boundary

Use synthetic secrets and isolated reference systems. Never run tool-execution
attacks against production accounts or customer systems from the public suite.

