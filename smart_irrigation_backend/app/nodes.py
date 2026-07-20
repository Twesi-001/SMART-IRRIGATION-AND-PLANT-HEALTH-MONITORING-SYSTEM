from flask import Blueprint, request, jsonify # type: ignore
from flask_jwt_extended import jwt_required, get_jwt_identity # type: ignore
from app.extensions import db
from app.models import SensorNode, User

nodes_bp = Blueprint("nodes", __name__, url_prefix="/api/nodes")


@nodes_bp.route("", methods=["GET"])
@jwt_required()  # ← Added JWT required
def list_nodes():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role == 'farmer':
        # Farmers see only their own nodes
        nodes = SensorNode.query.filter_by(user_id=current_user_id).all()
    else:
        # Admins and extension officers see all nodes
        nodes = SensorNode.query.all()
    
    return jsonify([n.to_dict() for n in nodes]), 200


@nodes_bp.route("", methods=["POST"])
@jwt_required()
def create_node():
    data = request.get_json(silent=True) or {}
    node_name = data.get("node_name")
    if not node_name:
        return jsonify({"error": "node_name is required"}), 400

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Only farmers and admins can create nodes
    if user.role not in ['farmer', 'admin']:
        return jsonify({"error": "Only farmers and admins can create nodes"}), 403

    node = SensorNode(
        node_name=node_name,
        location=data.get("location"),
        crop_type=data.get("crop_type"),
        moisture_threshold=data.get("moisture_threshold", 30.00),
        user_id=current_user_id if user.role == 'farmer' else data.get("user_id", current_user_id)
    )
    db.session.add(node)
    db.session.commit()
    return jsonify(node.to_dict()), 201


@nodes_bp.route("/<int:node_id>", methods=["GET"])
@jwt_required()  # ← Added JWT required
def get_node(node_id):
    """Get a specific node by ID"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    node = SensorNode.query.get(node_id)
    
    if not node:
        return jsonify({"error": f"node_id {node_id} does not exist"}), 404
    
    # Check permissions
    if user.role == 'farmer' and node.user_id != current_user_id:
        return jsonify({"error": "You don't have permission to view this node"}), 403
    
    return jsonify(node.to_dict()), 200


@nodes_bp.route("/<int:node_id>", methods=["PUT"])
@jwt_required()
def update_node(node_id):
    """Update a specific node"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    node = SensorNode.query.get(node_id)
    
    if not node:
        return jsonify({"error": f"node_id {node_id} does not exist"}), 404
    
    # Check permissions
    if user.role == 'farmer' and node.user_id != current_user_id:
        return jsonify({"error": "You don't have permission to update this node"}), 403
    
    if user.role == 'extension_officer':
        return jsonify({"error": "Extension officers cannot update nodes"}), 403
    
    data = request.get_json(silent=True) or {}
    
    if "node_name" in data:
        node.node_name = data["node_name"]
    if "location" in data:
        node.location = data["location"]
    if "crop_type" in data:
        node.crop_type = data["crop_type"]
    if "moisture_threshold" in data:
        node.moisture_threshold = data["moisture_threshold"]
    if "is_active" in data:
        node.is_active = data["is_active"]
    
    db.session.commit()
    return jsonify(node.to_dict()), 200


@nodes_bp.route("/<int:node_id>", methods=["DELETE"])
@jwt_required()
def delete_node(node_id):
    """Delete a specific node"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    node = SensorNode.query.get(node_id)
    
    if not node:
        return jsonify({"error": f"node_id {node_id} does not exist"}), 404
    
    # Only admins and the node owner can delete
    if user.role == 'farmer' and node.user_id != current_user_id:
        return jsonify({"error": "You don't have permission to delete this node"}), 403
    
    if user.role == 'extension_officer':
        return jsonify({"error": "Extension officers cannot delete nodes"}), 403
    
    if node.readings:
        return jsonify({"error": "Cannot delete node with existing readings"}), 400
    
    db.session.delete(node)
    db.session.commit()
    return jsonify({"message": f"node {node_id} deleted successfully"}), 200


@nodes_bp.route("/<int:node_id>/status", methods=["GET"])
@jwt_required()  # ← Added JWT required
def get_node_status(node_id):
    """Get a summary of node status including latest reading"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    node = SensorNode.query.get(node_id)
    
    if not node:
        return jsonify({"error": f"node_id {node_id} does not exist"}), 404
    
    # Check permissions
    if user.role == 'farmer' and node.user_id != current_user_id:
        return jsonify({"error": "You don't have permission to view this node"}), 403
    
    from app.models import SensorReading, Alert, PumpCommand
    from sqlalchemy import desc # type: ignore
    
    latest_reading = SensorReading.query.filter_by(node_id=node_id)\
                                       .order_by(desc(SensorReading.recorded_at)).first()
    
    active_alerts = Alert.query.filter_by(node_id=node_id, resolved=False).count()
    
    latest_pump = PumpCommand.query.filter_by(node_id=node_id)\
                                  .order_by(desc(PumpCommand.issued_at)).first()
    
    return jsonify({
        'node': node.to_dict(),
        'latest_reading': latest_reading.to_dict() if latest_reading else None,
        'active_alerts': active_alerts,
        'pump_status': latest_pump.command if latest_pump else 'OFF',
        'has_readings': latest_reading is not None
    }), 200