# Testing strategy

## Test layers

1. **Contract:** valid, invalid, duplicate, missing, unknown, and unsupported
   schema inputs.
2. **Evaluator unit:** metric boundaries, Unicode, empty evidence, critical
   rules, and evaluator plugin behavior.
3. **Engine integration:** absolute gates, baseline deltas, and exit decisions.
4. **Adapter:** Python, CLI, API, trace loader, store, and report rendering.
5. **Golden scenario:** passing, regressed, and adversarial fixtures remain
   stable and reviewable.

## Determinism

Core tests must not require a network or model credential. Provider evaluator
tests use recorded fixtures; optional live tests are separately marked and must
never gate contributor pull requests by default.

## Compatibility

Every published schema receives round-trip and historical-fixture tests before
the next schema version is introduced.

