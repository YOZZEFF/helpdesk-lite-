# HelpDesk Lite Architecture

## Sprint 1 Scope

- Ticket CRUD (create, list, update)
- Role-based auth (agent, manager, admin)
- SLA deadline calculation per priority
- Ticket assignment to agents
- SLA breach auto-escalation (NEW — Sprint 1)

## Non-Goals (Sprint 1)

- Real email/Slack integration (stubbed)
- Multi-channel ticket ingestion
- CSAT surveys
- SSO or LDAP auth
- Reporting dashboards

## Risks

- SLA deadline evaluation requires a scheduled job or trigger — not yet fully
  decided.
- Escalation may cause notification noise without cooldown logic.
- Manual escalation from UI also exists — auto-escalation must not duplicate.

## Key Decisions

- SLA policy is in-memory dict (configurable in future).
- `SLATracker.breached` is set explicitly, not computed on every read.
- Escalations are logged in `escalation_events` for audit trail.
- Auto-escalation is triggered on-demand via `POST /sla/check-escalations`
  (manager/admin). Background scheduling is a separate concern for Sprint 2.
- Breach detection uses a one-shot flag (`SLATracker.breached`). Once set, the
  ticket is not re-processed unless reset explicitly.
- `SLABreachEscalationService` accepts an optional `NotificationService`
  parameter for testability (DI pattern).
