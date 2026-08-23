# Privacy Policy

Last updated: 2026-08-02

RAGOps and its bundled plugin run locally by default. The project does not operate a hosted RAGOps service, create user accounts, collect telemetry, or transmit repository files, scenarios, traces, reports, or credentials to the project author.

RAGOps reads only the files and command arguments selected by the user. It may write reports, replay bundles, baselines, or local experiment records only when the user requests an operation that creates those artifacts. Those files remain in user-controlled storage.

Users may explicitly set `RAGOPS_USAGE_LOG` to write local usage events containing only a UTC timestamp, RAGOps version, top-level command name, and exit code. This is disabled by default, excludes command arguments and file paths, remains in user-controlled storage, and is never transmitted to the project author.

Optional provider or HTTP adapters can send data to an endpoint explicitly configured by the user. In that case, the endpoint operator's privacy terms apply. RAGOps does not enable a provider automatically and does not embed provider credentials.

Users control retention by deleting locally generated artifacts. For privacy questions, open an issue at https://github.com/thangldw/ragops/issues.
