# Five-minute demo walkthrough

## Prepare

```bash
pip install -e '.[dev,api]'
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
```

## 1. Establish the accepted build

Run `ragops evaluate` with the Japanese scenario and sample responses. Point to
the versioned thresholds, citations, cost, latency, and critical policies.

## 2. Introduce a candidate change

Run `ragops compare` using `regressed_responses.json`. Show that a candidate can
produce plausible text while failing a release or regression gate.

## 3. Inspect evidence

Open the Markdown or HTML report. Trace an aggregate failure to the individual
case, response, citation, metric, and policy rule.

## 4. Explain enterprise extension

Show the plugin protocol and portable trace contract. Explain how a customer
application exports evidence without moving retrieval or generation into the
RAGOps core.

## 5. Close with limitations

Lexical groundedness is a transparent baseline, not semantic truth. Current
red-team coverage is intentionally small. The benchmark and reference
deployment are the next milestone.

