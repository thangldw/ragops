# ADR 0009: Adopt the MIT License for repository HEAD

- Status: Accepted by product owner request
- Date: 2026-07-12

## Context

RAGOps is intended to be easy to evaluate, embed, extend, and redistribute as
an open-source developer tool. A short, widely recognized permissive license
reduces review friction for individual contributors and adopting teams.

The product owner explicitly requested the license change. The recorded Git
history currently identifies Thang Luu as the sole author; the owner remains
responsible for confirming that all contributed material can be relicensed.

## Decision

Repository HEAD and future releases use the MIT License. The complete local
release-decision loop defined in ADR 0004 remains open source: scenarios,
portable traces, deterministic evaluators, regression gates, reports, and
plugin interfaces are not moved behind a hosted service.

Previously published Apache-2.0 source and releases remain available under
their original license. This decision does not revoke those grants.

## Compatibility impact

There is no runtime, API, schema, metric, or release-gate behavior change.
License metadata, repository documentation, and the public showcase change
atomically for the next release.

## Consequences

- Reuse and redistribution have a shorter, familiar permission notice.
- The MIT License does not include Apache-2.0's explicit patent grant and
  termination language.
- Third-party components retain their own licenses and notices.
- Owner acceptance includes confirming rights to relicense repository HEAD.
