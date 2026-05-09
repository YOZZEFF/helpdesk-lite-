from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from ..services.sla_service import SLABreachEscalationService

sla_bp = Blueprint("sla", __name__, url_prefix="/sla")


@sla_bp.route("/check-escalations", methods=["POST"])
@jwt_required()
def run_sla_check():
    claims = get_jwt()
    if claims.get("role") not in ("manager", "admin"):
        return jsonify({"error": "Insufficient permissions"}), 403

    service = SLABreachEscalationService()
    escalated_ids = service.check_and_escalate()

    return jsonify({
        "escalated_ticket_ids": escalated_ids,
        "count": len(escalated_ids),
    })
