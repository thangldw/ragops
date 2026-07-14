# Product thesis

## Problem

Teams can demo RAG and agent applications quickly, but they struggle to answer
the production question: **is this version safe and useful enough to release?**
Quality evidence is fragmented across notebooks, vendor dashboards, prompt
logs, and manual reviews. Regressions are discovered after deployment, and
security checks are rarely connected to release decisions.

## Target users

- AI engineers shipping RAG or agent workflows.
- Engineering leads accountable for production quality.
- Forward Deployed Engineers proving a pilot is ready to scale.
- Security and governance reviewers who need reproducible evidence.

## Job to be done

When an AI workflow changes, run a versioned scenario and receive an
explainable release decision covering quality, operational budgets, and
high-risk policy failures.

## Product wedge

Lead with a local-first, CI-friendly evaluation runner. It accepts portable
scenarios, responses, traces, and optional external metrics; runs deterministic
evaluators; and emits stable release evidence. Provider-backed judging and
hosted collaboration remain optional layers, not prerequisites for value.

## Open-core direction

The scenario format, runner, deterministic evaluators, CLI, and report schema
remain open source under the MIT License. A complete release decision must stay
possible without a hosted account. Potential commercial layers include managed
workspaces, datasets, ingestion, access controls, audit retention, trend
analysis, and enterprise integrations.

## North-star outcome

Reduce the time from an AI change to a defensible go/no-go decision while
lowering the rate of quality and security regressions reaching production.
