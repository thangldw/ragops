# Discovery and scope

## Ambiguous request

“Use AI to help Japanese field engineers troubleshoot machines faster.”

## Discovery questions

- Which incident workflow consumes the most engineer time?
- Which manuals and policies are authoritative, current, and permissioned?
- When must the system abstain, escalate, or request approval?
- Which actions are advisory versus externally consequential?
- What baseline exists for resolution time, escalation, and search effort?
- Who owns a wrong answer and the production go/no-go decision?

## MVP decision

Limit scope to A1000/B2000 troubleshooting, escalation policy, parts context,
role-filtered evidence, cited answers, and approval-aware decisions. Evaluate
offline before connecting a model or enterprise identity provider.

## Success criteria

- Required citation coverage and precision meet scenario thresholds.
- No restricted document is retrieved for an unauthorized role.
- External communication produces `request_approval`, never execution.
- Candidate changes are compared against an accepted trace baseline.
- Pilot hypothesis: reduce median search time by 30% without increasing unsafe
  escalation or permission incidents.

