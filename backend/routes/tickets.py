from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from ..models.ticket import Ticket
from ..models.sla_tracker import SLATracker
from ..models.user import User
from ..models import db

tickets_bp = Blueprint("tickets", __name__, url_prefix="/tickets")


@tickets_bp.route("", methods=["GET"])
@jwt_required()
def list_tickets():
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    return jsonify([{
        "id": t.id,
        "title": t.title,
        "status": t.status,
        "priority": t.priority,
        "assigned_to": t.assigned_to,
        "created_at": t.created_at.isoformat(),
    } for t in tickets])


@tickets_bp.route("", methods=["POST"])
@jwt_required()
def create_ticket():
    data = request.get_json()
    ticket = Ticket(
        title=data["title"],
        description=data.get("description", ""),
        priority=data.get("priority", "medium"),
        status="open",
    )
    db.session.add(ticket)
    db.session.flush()

    sla = SLATracker(
        ticket_id=ticket.id,
        sla_deadline=SLATracker.calculate_deadline(ticket.priority),
    )
    db.session.add(sla)
    db.session.commit()

    return jsonify({"id": ticket.id}), 201


@tickets_bp.route("/<int:ticket_id>/assign", methods=["POST"])
@jwt_required()
def assign_ticket(ticket_id: int):
    data = request.get_json()
    ticket = Ticket.query.get_or_404(ticket_id)
    user = User.query.get_or_404(data["user_id"])
    ticket.assigned_to = user.id
    db.session.commit()
    return jsonify({"message": f"Ticket assigned to {user.name}"})
