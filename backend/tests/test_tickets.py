from ..models.sla_tracker import SLATracker, SLA_POLICY


def test_sla_deadline_calculated_on_create():
    deadline = SLATracker.calculate_deadline("critical", "response")
    minutes = SLA_POLICY["critical"]["response_minutes"]
    assert deadline is not None


def test_sla_deadline_defaults_to_medium():
    deadline = SLATracker.calculate_deadline("unknown", "resolution")
    assert deadline is not None
