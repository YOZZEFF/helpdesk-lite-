from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from dataclasses import dataclass

db = SQLAlchemy()


@dataclass
class EscalationEvent(db.Model):
    __tablename__ = "escalation_events"

    id: int
    ticket_id: int
    escalated_by: int
    from_tier: int
    to_tier: int
    reason: str
    created_at: str

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(
        db.Integer, db.ForeignKey("tickets.id"), nullable=False
    )
    escalated_by = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    from_tier = db.Column(db.Integer, nullable=False)
    to_tier = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(500), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    ticket = db.relationship("Ticket", backref="escalation_events")
    escalated_by_user = db.relationship("User", backref="escalations_initiated")
