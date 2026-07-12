# Five-minute demo walkthrough

## Prepare

```bash
pip install -e '.[dev,api]'
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
```

## 1. Run the adoption path

```bash
ragops demo --output ragops-demo
```

Open `ragops-demo/release-report.html`. Explain that command success and
candidate PASS/BLOCK are separate concepts: the demo completed successfully
because it reproduced an expected blocked regression.

## 2. Establish the accepted build

Run `ragops evaluate` with the Japanese scenario and sample responses. Point to
the versioned thresholds, citations, cost, latency, and critical policies.

## 3. Introduce a candidate change

Run `ragops compare` using `regressed_responses.json`. Show that a candidate can
produce plausible text while failing a release or regression gate.

## 4. Inspect evidence

Open the Markdown or HTML report. Trace an aggregate failure to the individual
case, response, citation, metric, and policy rule.

## 5. Explain enterprise extension

Show the plugin protocol and portable trace contract. Explain how a customer
application exports evidence without moving retrieval or generation into the
RAGOps core.

## 6. Close with limitations

Lexical groundedness is a transparent baseline, not semantic truth. The
reference ACL and graph are simulations, attack metadata is not fully executed
end-to-end, and the local control plane is not a hosted production service.
