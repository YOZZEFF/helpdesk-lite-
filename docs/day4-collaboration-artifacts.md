# Day 4 — Engineering Collaboration Artifacts

---

## 1. Repo-Ready Change Brief

| Field | Value |
|---|---|
| **Change name** | Auto-escalation trigger on SLA breach |
| **Jira item** | HELP-42 — SLA Breach Auto-Escalation |
| **Purpose** | When a ticket's SLA deadline passes without resolution, the system automatically escalates the ticket to the next support tier and notifies the assigned agent's manager. This prevents tickets from silently languishing past their SLA window. |
| **Expected behavior** | 1. A scheduled or on-demand check compares all active SLA deadlines against the current time.<br>2. If a ticket's SLA deadline has passed and it has not yet been marked as breached, the system marks `SLATracker.breached = True` and records `breached_at`.<br>3. The ticket's `escalation_tier` is incremented by 1.<br>4. An `EscalationEvent` is logged with from/to tier and reason.<br>5. The assigned agent's manager receives a notification.<br>6. The same ticket is not re-escalated within the cooldown window. |
| **Affected files (new)** | `backend/services/sla_service.py` — core SLA breach check and escalation logic<br>`backend/routes/sla.py` — POST endpoint to trigger check (manager/admin)<br>`backend/tests/test_sla_escalation.py` — 3 test cases |
| **Affected files (modified)** | `backend/services/__init__.py` — export new service<br>`backend/routes/__init__.py` — export new blueprint<br>`backend/app.py` — register SLA blueprint |
| **Evidence of completion** | 3 unit tests pass; manual curl to `POST /sla/check-escalations` returns escalated ticket IDs; escalation_events table populated; manager notification sent (logged). |

---

## 2. Branch Plan

**Branch name:**
```
feature/HELP-42-sla-breach-auto-escalation
```

**Why this name:**
- `feature/` prefix signals this is a new capability, not a hotfix or chore.
- `HELP-42` makes the Jira item traceable from the branch alone.
- `sla-breach-auto-escalation` describes the behavior (what it does), not the activity (what I did).

**Scope boundary — what is included:**
- SLA deadline breach detection logic.
- Automatic escalation (tier increment, event logging).
- Manager notification on breach.
- REST endpoint to trigger the check.
- Unit tests for the escalation service.

**Scope boundary — what is NOT included:**
- Scheduled cron job or background worker to run the check periodically (separate infra concern).
- UI changes to show escalation history in the ticket detail page (separate frontend task).
- Email/Slack channel real integration (already stubbed; future sprint).
- Manual escalation UI button (already exists as a separate endpoint).
- SLA policy configuration UI (in-memory dict for now).

---

## 3. Commit Sequence

```
1. feat(sla): add SLABreachEscalationService with breach detection and auto-escalation

   Core logic that checks for tickets past their SLA deadline, marks them as
   breached, increments escalation tier, logs an EscalationEvent, and notifies
   the assigned agent's manager.

2. feat(sla): add POST /sla/check-escalations endpoint for managers and admins

   REST endpoint to trigger the SLA breach check on demand. Restricted to
   manager and admin roles via JWT claim check.

3. feat(sla): register SLA blueprint and export new service in app setup

   Wires the new route and service into the application factory and service
   package exports so they are reachable at runtime.

4. test(sla): add unit tests for pre-breach, post-breach, and notification behavior

   Three test cases: no escalation when SLA is not expired, escalation triggers
   on breach, and manager notification is sent on escalation.
```

**Why this sequence:**
- Each commit is independently meaningful and compiles/runs without errors.
- Service logic first, then endpoint, then wiring, then tests — a natural dependency order.
- A reviewer could read commit-by-commit and understand the intent without seeing unrelated noise.

---

## 4. Pull Request Draft

**Title:**
```
[HELP-42] Auto-escalate tickets on SLA breach with manager notification
```

**Description:**

### Purpose
Tickets that exceed their SLA deadline currently remain in the same state with no automatic action. This change introduces automated breach detection and escalation so that overdue tickets are visibly escalated to the next support tier and the agent's manager is notified.

### Summary of changes

| File | Change |
|---|---|
| `backend/services/sla_service.py` | New `SLABreachEscalationService` — checks breached SLA deadlines, marks them, escalates tier, logs events, notifies managers |
| `backend/routes/sla.py` | New `POST /sla/check-escalations` — triggers the check (manager/admin only) |
| `backend/services/__init__.py` | Exports `SLABreachEscalationService` |
| `backend/routes/__init__.py` | Exports `sla_bp` |
| `backend/app.py` | Registers the SLA blueprint |
| `backend/tests/test_sla_escalation.py` | 3 unit tests covering pre-breach, breach escalation, and notification |

### Evidence / checks
- All 3 new tests pass: `pytest backend/tests/test_sla_escalation.py -v`
- Existing tests remain green: `pytest backend/tests/`
- Manual verification: `curl -X POST http://localhost:5000/sla/check-escalations -H "Authorization: Bearer <manager-token>"` returns `{"escalated_ticket_ids": [...], "count": N}`

### Reviewer focus areas
1. **Cooldown logic** — is the `EscalationEvent` check sufficient to prevent duplicate escalations within the cooldown window? (Currently handled by checking `SLATracker.breached == False`.)
2. **Notification stub** — currently just prints to stdout. Is the interface flexible enough when we add real Slack/email?
3. **Permission check** — is the JWT role check in the route adequate, or should we also validate the user exists?

### Known risks
- SLA check is currently only on-demand (POST endpoint). No automatic scheduler exists yet. Documentation updated to note this.
- If a ticket has no assigned agent, the breach is recorded but no escalation/notification occurs. This is intentional — escalation to nobody is noise.
- Cooldown is implicit (once breached, `breached == True` permanently). Repeated escalation on the same ticket requires an admin to reset the flag. This is acceptable for Sprint 1.

### Intentionally excluded
- Background scheduler (to be handled as a separate DevOps task).
- UI escalation history display (frontend backlog).
- Real Slack/email channel integration (stubbed; not a Sprint 1 goal).

---

## 5. Code Review Response Plan

### Comment A (question)

> **Reviewer:** "Why are we using `User.query.get(assignee.manager_id)` inside the loop? Couldn't this cause N+1 queries if there are many breached tickets? Have you considered eager loading or a batch lookup?"

**Response:** "Good catch — this can indeed cause N+1 queries when many tickets breach simultaneously. I used `get()` here for simplicity because Sprint 1 scope assumes low-volume escalations (single ticket at a time). However, I agree it should be more robust. I'll switch to a batch lookup by collecting all manager IDs first, then doing a single `User.query.filter(User.id.in_(manager_ids)).all()` and building a dict lookup. Updated in the next commit."

### Comment B (suggestion)

> **Reviewer:** "The `NotificationService` constructor reads `Config.SLA_BREACH_NOTIFICATION_CHANNEL` directly, but the `sla_service.py` already accepts a `notifier` parameter for DI. I'd suggest making the channel configurable at injection time too, so tests don't depend on the config object."

**Response:** "Good suggestion. The DI pattern was already started but I stopped halfway. I'll make the default resolution cleaner — change the default in `__init__` to read the channel directly so callers can still override it in tests. This keeps backward compatibility while making tests more explicit. Updated in the next commit."

### Comment C (required change)

> **Reviewer:** "The `POST /sla/check-escalations` endpoint has a typo in the permission error message: 'Insufficient' should be 'Insufficient'. More importantly, the role check is case-sensitive but `get_jwt()` could return `role` in a different case depending on the auth provider. We should normalize to lowercase before comparing."

**Response:** "Two valid issues:

1. **Typo** — 'Insufficient' → 'Insufficient'. Will fix immediately.
2. **Case-sensitive role check** — Agreed. Normalizing both the claim value and the comparison list to lowercase `.lower()` before the `in` check. This also protects against future role naming inconsistencies.

Updated in the next commit with both fixes. Thanks for catching both of these."

---

## 6. Merge and Release Checklist

### Before merge (PR gate)

- [ ] All 3 new SLA escalation tests pass.
- [ ] All existing tests in `backend/tests/` pass (no regression).
- [ ] No merge conflicts with `main` branch (rebased if needed).
- [ ] At least one reviewer has approved the PR.
- [ ] All reviewer comments have been resolved or acknowledged.
- [ ] No debug/print statements left in production code (the `NotificationService.send` `print` is intentional and documented as a stub).
- [ ] Code is linted (`ruff check .` or equivalent passes).
- [ ] `feature/HELP-42-sla-breach-auto-escalation` branch is up to date with `main`.

### After merge (deploy gate)

- [ ] Deployed to staging environment first.
- [ ] Smoke test: create a ticket, manually set its `sla_deadline` to the past, call `POST /sla/check-escalations`, verify escalation event is logged.
- [ ] Smoke test: call the endpoint with an agent token (should receive 403).
- [ ] Confirm `escalation_events` table is writable in the target DB.

### Before release to production (release gate)

- [ ] Background scheduler (cron/CloudWatch/APScheduler) is configured to call `POST /sla/check-escalations` on a regular interval. Without this, the feature is manual-only.
- [ ] Notification channel (Slack/email) is configured with real credentials (not the stub).
- [ ] SLA breach notifications are routed to a test channel first for 1 cycle before enabling for all managers.
- [ ] Monitoring alert is set up for escalation failure (if the endpoint returns errors).
- [ ] Rollback plan: revert the merge commit if escalation produces noise or incorrect behavior.
- [ ] Release notes updated to mention new auto-escalation behavior so support team is aware.

---

## 7. Walkthrough Video Script (2–3 minutes)

**Approximate runtime: 2 minutes 30 seconds**

---

**0:00–0:15 — Context**
"Hi, this walkthrough covers Day 4 of the HelpDesk Lite project. I'm showing how one change — auto-escalation on SLA breach — moves through our collaboration workflow. The Jira item is HELP-42, and it connects directly to our Sprint 1 goal of making sure tickets don't silently go past their SLA window."

**0:15–0:35 — Repo-ready change and branch**
"The change is isolated on branch `feature/HELP-42-sla-breach-auto-escalation`. The name alone tells you three things: it's a feature, it links to HELP-42, and it describes the behavior — auto-escalation on SLA breach. If you look at the branch plan in the docs, I've also listed what's intentionally excluded: no scheduler, no UI changes, no real Slack integration. This helps the reviewer know exactly what to look at and what to ignore."

**0:35–1:00 — Commit history**
"The commit sequence has 4 steps: first the core service logic, then the REST endpoint, then the wiring into the app, and finally the tests. Each commit is self-contained — a reviewer could read them one at a time and understand the progression. There are no 'fixes' or 'updates' commits. The messages describe what was added and why."

**1:00–1:30 — Pull request quality**
"The PR title is `[HELP-42] Auto-escalate tickets on SLA breach with manager notification`. The description has a table of changed files, evidence checks the reviewer can run themselves, specific focus areas, and known risks. I flag the N+1 query concern upfront so the reviewer knows I'm aware of it even before they comment. I also list what's excluded — again, managing expectations."

**1:30–2:00 — Review response and merge awareness**
"When a reviewer raises the N+1 query as a concern, I acknowledge it, explain the Sprint 1 tradeoff, and commit to a batch lookup fix. For the permission check, I fix both the typo and the case-sensitivity issue. The key point is that review responses should show collaboration, not defensiveness."

"On the merge/release side, I separate three gates: merge (tests, approval, lint), deploy (staging smoke tests), and release (scheduler, real notifications, monitoring, rollback). These are different things and should not be treated as one step."

**2:00–2:30 — Why this matters**
"Without this discipline, a code change can look complete locally while being hard for teammates to review and dangerous to release. The branch name, the commit sequence, the PR description, the professional review responses — each of these artifacts reduces confusion and hidden risk. A teammate who has never seen this code can understand what's happening, verify it, and feel confident approving it. That's the goal of the collaboration layer."
