# HelpDesk Lite

Lightweight internal support ticketing workspace.

**Sprint 1 scope:** Ticket creation, assignment, priority management, SLA tracking, and escalation workflow.

## Architecture

- **Backend:** Python/Flask REST API
- **Database:** PostgreSQL (via SQLAlchemy ORM)
- **Auth:** JWT-based role authentication (Agent, Manager, Admin)

## Key Models

- `Ticket` — core support request with status, priority, assigned agent, timestamps
- `User` — agent, manager, admin roles
- `SLATracker` — per-ticket SLA policy and deadline tracking
- `EscalationEvent` — log of escalation actions (new in Sprint 1)

## Running Locally

```bash
pip install -r requirements.txt
flask run
```

## Testing

```bash
pytest backend/tests/
```
