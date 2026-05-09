from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from dataclasses import dataclass

db = SQLAlchemy()


@dataclass
class Ticket(db.Model):
    __tablename__ = "tickets"

    id: int
    title: str
    description: str
    status: str
    priority: str
    created_at: str
    assigned_to: int | None

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.String(50), nullable=False, default="open"
    )
    priority = db.Column(
        db.String(50), nullable=False, default="medium"
    )
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    assigned_to = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )
    escalated_at = db.Column(db.DateTime, nullable=True)
    escalation_tier = db.Column(db.Integer, default=1)

    assignee = db.relationship("User", backref="assigned_tickets")
