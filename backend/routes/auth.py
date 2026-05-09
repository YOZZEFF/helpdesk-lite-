from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from ..models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "name": user.name},
    )
    return jsonify({"token": token, "user": {"id": user.id, "role": user.role}})
