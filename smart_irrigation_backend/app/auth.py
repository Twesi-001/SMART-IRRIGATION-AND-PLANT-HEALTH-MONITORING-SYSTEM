from flask import Blueprint, request, jsonify # type: ignore
from flask_jwt_extended import create_access_token # type: ignore
from app.extensions import db
from app.models import User, SensorNode, FarmerNode  # ← ADDED SensorNode, FarmerNode

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    role = data.get("role", "farmer")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    if role not in ("farmer", "extension_officer", "admin"):
        return jsonify({"error": "invalid role"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "username already taken"}), 409

    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # ✅ AUTO-ASSIGN ALL NODES TO NEW FARMERS
    if user.role == 'farmer':
        all_nodes = SensorNode.query.all()
        for node in all_nodes:
            farmer_node = FarmerNode(
                farmer_id=user.id,
                node_id=node.id,
                custom_name=f"{user.username}'s {node.crop_type or 'Garden'}"
            )
            db.session.add(farmer_node)
        db.session.commit()
        print(f"✅ Assigned {len(all_nodes)} nodes to new farmer: {user.username}")

    return jsonify(user.to_dict()), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "invalid credentials"}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "username": user.username,
            "role": user.role,
            "user_id": user.id
        },
    )
    return jsonify({"access_token": access_token, "user": user.to_dict()}), 200