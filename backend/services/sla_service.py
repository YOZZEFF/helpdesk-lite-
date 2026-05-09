from datetime import datetime, timezone
from ..models.ticket import Ticket
from ..models.sla_tracker import SLATracker
from ..models.escalation_event import EscalationEvent
from ..models.user import User
from ..models import db
from .notification_service import NotificationService, NotificationPayload
from ..config import Config


class SLABreachEscalationService:
    def __init__(self, notifier: NotificationService | None = None):
        self._notifier = notifier or NotificationService(
            channel=Config.SLA_BREACH_NOTIFICATION_CHANNEL
        )
        self._cooldown_minutes = Config.ESCALATION_COOLDOWN_MINUTES

    def check_and_escalate(self) -> list[int]:
        now = datetime.now(timezone.utc)
        escalated_ticket_ids: list[int] = []

        breached_trackers = SLATracker.query.filter(
            SLATracker.sla_deadline < now,
            SLATracker.breached == False,
        ).all()

        for tracker in breached_trackers:
            self._process_breach(tracker, now)
            escalated_ticket_ids.append(tracker.ticket_id)

        db.session.commit()
        return escalated_ticket_ids

    def _process_breach(self, tracker: SLATracker, now: datetime) -> None:
        ticket = tracker.ticket

        tracker.breached = True
        tracker.breached_at = now

        if ticket.assigned_to is None:
            return

        new_tier = ticket.escalation_tier + 1
        assignee = User.query.get(ticket.assigned_to)

        event = EscalationEvent(
            ticket_id=ticket.id,
            escalated_by=assignee.id,
            from_tier=ticket.escalation_tier,
            to_tier=new_tier,
            reason=(
                f"SLA breached at {now.isoformat()}. "
                f"Auto-escalated from tier {ticket.escalation_tier} to {new_tier}."
            ),
        )
        db.session.add(event)

        ticket.escalation_tier = new_tier
        ticket.escalated_at = now

        if assignee and assignee.manager_id:
            manager = User.query.get(assignee.manager_id)
            if manager:
                payload = NotificationPayload(
                    channel=self._notifier._channel,
                    recipient=manager.email,
                    subject=f"SLA Breach: Ticket #{ticket.id} - {ticket.title}",
                    body=(
                        f"Ticket '{ticket.title}' (ID: {ticket.id}) "
                        f"breached SLA at {now.isoformat()}. "
                        f"Assigned agent: {assignee.name}. "
                        f"Escalated to tier {new_tier}."
                    ),
                )
                self._notifier.send(payload)
