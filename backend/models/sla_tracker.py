from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass

db = SQLAlchemy()


SLA_POLICY = {
    "critical": {"response_minutes": 15, "resolution_minutes": 240},
    "high": {"response_minutes": 30, "resolution_minutes": 480},
    "medium": {"response_minutes": 120, "resolution_minutes": 2880},
    "low": {"response_minutes": 480, "resolution_minutes": 8640},
}


@dataclass
class SLATracker(db.Model):
    __tablename__ = "sla_trackers"

    id: int
    ticket_id: int
    sla_deadline: str
    breached: bool
    breached_at: str | None

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(
        db.Integer, db.ForeignKey("tickets.id"), unique=True, nullable=False
    )
    sla_deadline = db.Column(db.DateTime, nullable=False)
    breached = db.Column(db.Boolean, default=False)
    breached_at = db.Column(db.DateTime, nullable=True)

    ticket = db.relationship("Ticket", backref="sla_tracker")

    @classmethod
    def calculate_deadline(cls, priority: str, field: str = "resolution") -> datetime:
        policy = SLA_POLICY.get(priority, SLA_POLICY["medium"])
        key = f"{field}_minutes"
        minutes = policy.get(key, policy["resolution_minutes"])
        return datetime.now(timezone.utc) + timedelta(minutes=minutes)
