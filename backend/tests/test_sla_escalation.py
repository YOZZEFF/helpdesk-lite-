from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch
from ..services.sla_service import SLABreachEscalationService


def test_no_breach_when_sla_not_expired():
    mock_tracker = MagicMock()
    mock_tracker.sla_deadline = datetime.now(timezone.utc) + timedelta(hours=1)
    mock_tracker.breached = False

    service = SLABreachEscalationService()
    with patch.object(
        service, "_process_breach"
    ) as mock_process:
        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = [mock_tracker]
        with patch(
            "backend.services.sla_service.SLATracker.query", mock_query
        ):
            result = service.check_and_escalate()
            mock_process.assert_not_called()
            assert result == []


def test_breach_triggers_escalation():
    ticket = MagicMock()
    ticket.id = 42
    ticket.escalation_tier = 1
    ticket.assigned_to = 1
    ticket.title = "Test ticket"

    tracker = MagicMock()
    tracker.ticket = ticket
    tracker.sla_deadline = datetime.now(timezone.utc) - timedelta(minutes=5)
    tracker.breached = False
    tracker.ticket_id = 42

    service = SLABreachEscalationService()
    with patch.object(service, "_process_breach") as mock_process:
        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = [tracker]
        with patch(
            "backend.services.sla_service.SLATracker.query", mock_query
        ):
            result = service.check_and_escalate()
            mock_process.assert_called_once()
            assert result == [42]


def test_escalation_sends_notification():
    manager = MagicMock()
    manager.email = "manager@example.com"
    manager.id = 99

    assignee = MagicMock()
    assignee.id = 1
    assignee.name = "Alice Agent"
    assignee.manager_id = 99

    ticket = MagicMock()
    ticket.id = 42
    ticket.title = "Login broken"
    ticket.escalation_tier = 1
    ticket.assigned_to = 1

    tracker = MagicMock()
    tracker.ticket = ticket
    tracker.sla_deadline = datetime.now(timezone.utc) - timedelta(minutes=5)
    tracker.breached = False
    tracker.ticket_id = 42

    mock_notifier = MagicMock()
    service = SLABreachEscalationService(notifier=mock_notifier)

    mock_query = MagicMock()
    mock_query.filter.return_value.all.return_value = [tracker]

    with (
        patch(
            "backend.services.sla_service.SLATracker.query", mock_query
        ),
        patch(
            "backend.services.sla_service.User.query.get",
            side_effect=lambda uid: {
                1: assignee,
                99: manager,
            }.get(uid),
        ),
    ):
        result = service.check_and_escalate()

        mock_notifier.send.assert_called_once()
        args = mock_notifier.send.call_args[0][0]
        assert args.recipient == "manager@example.com"
        assert "SLA Breach" in args.subject
        assert result == [42]
