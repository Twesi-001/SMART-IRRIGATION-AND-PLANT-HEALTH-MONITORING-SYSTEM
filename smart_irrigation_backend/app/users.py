from flask import Blueprint, request, jsonify # type: ignore
from flask_jwt_extended import jwt_required, get_jwt_identity # type: ignore
from app.extensions import db
from app.models import User, SensorNode

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("", methods=["GET"])
@jwt_required()
def get_users():
    """Get all users (Extension Officers and Admins only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Only extension officers and admins can see all users
    if user.role not in ['extension_officer', 'admin']:
        return jsonify({"error": "Unauthorized"}), 403
    
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200


@users_bp.route("/farmers", methods=["GET"])
@jwt_required()
def get_farmers():
    """Get all farmers with node counts (Extension Officers and Admins only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Only extension officers and admins can see farmers
    if user.role not in ['extension_officer', 'admin']:
        return jsonify({"error": "Unauthorized"}), 403
    
    farmers = User.query.filter_by(role='farmer').all()
    result = []
    for farmer in farmers:
        nodes = SensorNode.query.filter_by(user_id=farmer.id).all()
        result.append({
            "user": farmer.to_dict(),
            "node_count": len(nodes),
            "nodes": [n.to_dict() for n in nodes]
        })
    
    return jsonify(result), 200


@users_bp.route("/<int:user_id>/role", methods=["PUT"])
@jwt_required()
def update_user_role(user_id):
    """Update user role (Admins only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Only admins can change roles
    if user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json(silent=True) or {}
    new_role = data.get("role")
    
    if new_role not in ['farmer', 'extension_officer', 'admin']:
        return jsonify({"error": "Invalid role"}), 400
    
    target_user.role = new_role
    db.session.commit()
    
    return jsonify(target_user.to_dict()), 200