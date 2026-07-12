# Controlled rollout plan

## Phase 0 — offline acceptance

Run synthetic and customer-reviewed golden cases. Establish baseline traces,
failure taxonomy, security boundary, and named production decision owner.

## Phase 1 — shadow mode

Generate recommendations without showing them to field engineers. Compare with
actual resolutions and review permission, citation, latency, and abstention
failures weekly.

## Phase 2 — 20-user pilot

Expose cited advisory answers to a single product/site cohort. External actions
remain disabled. Track adoption, successful task completion, time-to-answer,
escalation precision, user feedback, and cost per successful task.

## Phase 3 — controlled scale

Expand only after quality and workflow guardrails hold for four weeks. Introduce
SSO/ACL integration, incident response, audit retention, and rollback ownership.

## Go/no-go

Scale when offline gates pass, no critical permission/action incident occurs,
and measured task-time improvement exceeds the agreed minimum. Hold or redesign
when adoption is low despite quality, because deployment success is a workflow
outcome rather than an answer score.

