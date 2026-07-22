from datetime import datetime
from flask import Blueprint, request, jsonify # type: ignore
from flask_jwt_extended import jwt_required, get_jwt_identity # type: ignore
from app.extensions import db
from app.models import Alert, SensorNode, User, FarmerNode
from app.device_auth import require_device_key

alerts_bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")


@alerts_bp.route("", methods=["GET"])
def list_alerts():
    node_id = request.args.get("node_id", 1, type=int)
    resolved = request.args.get("resolved")

    query = Alert.query.filter_by(node_id=node_id)
    if resolved is not None:
        query = query.filter_by(resolved=(resolved.lower() == "true"))

    alerts = query.order_by(Alert.created_at.desc()).all()
    return jsonify([a.to_dict() for a in alerts]), 200


@alerts_bp.route("", methods=["POST"])
@require_device_key
def create_alert():
    """Called by the automated monitoring logic."""
    data = request.get_json(silent=True) or {}
    node_id = data.get("node_id", 1)
    alert_type = data.get("alert_type")
    message = data.get("message")
    severity = data.get("severity", "WARNING")

    if not alert_type or not message:
        return jsonify({"error": "alert_type and message are required"}), 400

    if not SensorNode.query.get(node_id):
        return jsonify({"error": f"node_id {node_id} does not exist"}), 404

    alert = Alert(node_id=node_id, alert_type=alert_type, message=message, severity=severity)
    db.session.add(alert)
    db.session.commit()

    return jsonify(alert.to_dict()), 201


@alerts_bp.route("/<int:alert_id>/resolve", methods=["POST"])
@jwt_required()
def resolve_alert(alert_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({"error": "alert not found"}), 404
    
    # ✅ Check permission for farmers
    if user.role == 'farmer':
        farmer_node = FarmerNode.query.filter_by(
            farmer_id=current_user_id,
            node_id=alert.node_id
        ).first()
        node = SensorNode.query.get(alert.node_id)
        if not farmer_node and (not node or node.user_id != current_user_id):
            return jsonify({"error": "You don't have permission to resolve this alert"}), 403

    alert.resolved = True
    alert.resolved_at = datetime.utcnow()
    db.session.commit()

    return jsonify(alert.to_dict()), 200


@alerts_bp.route("/<int:alert_id>", methods=["GET"])
@jwt_required()
def get_alert(alert_id):
    """Get a specific alert by ID"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({"error": "alert not found"}), 404
    
    # ✅ Check permission for farmers
    if user.role == 'farmer':
        farmer_node = FarmerNode.query.filter_by(
            farmer_id=current_user_id,
            node_id=alert.node_id
        ).first()
        node = SensorNode.query.get(alert.node_id)
        if not farmer_node and (not node or node.user_id != current_user_id):
            return jsonify({"error": "You don't have permission to view this alert"}), 403
    
    return jsonify(alert.to_dict()), 200


@alerts_bp.route("/<int:alert_id>", methods=["DELETE"])
@jwt_required()
def delete_alert(alert_id):
    """Delete an alert (permanent removal)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({"error": "alert not found"}), 404
    
    # ✅ Check permission for farmers
    if user.role == 'farmer':
        farmer_node = FarmerNode.query.filter_by(
            farmer_id=current_user_id,
            node_id=alert.node_id
        ).first()
        node = SensorNode.query.get(alert.node_id)
        if not farmer_node and (not node or node.user_id != current_user_id):
            return jsonify({"error": "You don't have permission to delete this alert"}), 403
    
    db.session.delete(alert)
    db.session.commit()
    return jsonify({"message": f"alert {alert_id} deleted successfully"}), 200


@alerts_bp.route("/resolve-all", methods=["POST"])
@jwt_required()
def resolve_all_alerts():
    """Resolve all alerts for a node"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    node_id = request.args.get("node_id", 1, type=int)
    
    if not SensorNode.query.get(node_id):
        return jsonify({"error": f"node_id {node_id} does not exist"}), 404
    
    # ✅ Check permission for farmers
    if user.role == 'farmer':
        farmer_node = FarmerNode.query.filter_by(
            farmer_id=current_user_id,
            node_id=node_id
        ).first()
        node = SensorNode.query.get(node_id)
        if not farmer_node and (not node or node.user_id != current_user_id):
            return jsonify({"error": "You don't have permission to resolve alerts for this node"}), 403
    
    alerts = Alert.query.filter_by(node_id=node_id, resolved=False).all()
    count = len(alerts)
    
    for alert in alerts:
        alert.resolved = True
        alert.resolved_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({
        'message': f'Resolved {count} alerts for node {node_id}',
        'resolved_count': count,
        'node_id': node_id
    }), 200


@alerts_bp.route("/unresolved", methods=["GET"])
@jwt_required()
def get_unresolved_alerts():
    """Get all unresolved alerts for the current user's nodes"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    node_id = request.args.get("node_id", type=int)
    
    # ✅ For farmers, only show alerts for their nodes
    if user.role == 'farmer':
        farmer_nodes = FarmerNode.query.filter_by(farmer_id=current_user_id).all()
        farmer_node_ids = [fn.node_id for fn in farmer_nodes]
        
        direct_nodes = SensorNode.query.filter_by(user_id=current_user_id).all()
        direct_node_ids = [n.id for n in direct_nodes]
        
        allowed_node_ids = list(set(farmer_node_ids + direct_node_ids))
        
        if not allowed_node_ids:
            return jsonify([]), 200
        
        query = Alert.query.filter_by(resolved=False)
        if node_id:
            if node_id not in allowed_node_ids:
                return jsonify({"error": "You don't have permission to view alerts for this node"}), 403
            query = query.filter_by(node_id=node_id)
        else:
            query = query.filter(Alert.node_id.in_(allowed_node_ids))
        
        alerts = query.order_by(Alert.created_at.desc()).all()
        return jsonify([a.to_dict() for a in alerts]), 200
    
    else:
        # Admins and extension officers see all alerts
        query = Alert.query.filter_by(resolved=False)
        if node_id:
            query = query.filter_by(node_id=node_id)
        alerts = query.order_by(Alert.created_at.desc()).all()
        return jsonify([a.to_dict() for a in alerts]), 200


@alerts_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_alerts_summary():
    """Get summary of alerts for the current user's nodes"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    from sqlalchemy import func # type: ignore
    
    if user.role == 'farmer':
        farmer_nodes = FarmerNode.query.filter_by(farmer_id=current_user_id).all()
        farmer_node_ids = [fn.node_id for fn in farmer_nodes]
        
        direct_nodes = SensorNode.query.filter_by(user_id=current_user_id).all()
        direct_node_ids = [n.id for n in direct_nodes]
        
        allowed_node_ids = list(set(farmer_node_ids + direct_node_ids))
        
        if not allowed_node_ids:
            return jsonify({'total_unresolved': 0, 'by_node': []}), 200
        
        summary = db.session.query(
            Alert.node_id,
            func.count(Alert.id).label('unresolved_count')
        ).filter(
            Alert.resolved == False,
            Alert.node_id.in_(allowed_node_ids)
        ).group_by(Alert.node_id).all()
        
        total_unresolved = Alert.query.filter(
            Alert.resolved == False,
            Alert.node_id.in_(allowed_node_ids)
        ).count()
        
    else:
        summary = db.session.query(
            Alert.node_id,
            func.count(Alert.id).label('unresolved_count')
        ).filter_by(resolved=False).group_by(Alert.node_id).all()
        
        total_unresolved = Alert.query.filter_by(resolved=False).count()
    
    return jsonify({
        'total_unresolved': total_unresolved,
        'by_node': [{'node_id': s.node_id, 'count': s.unresolved_count} for s in summary]
    }), 200


@alerts_bp.route("/recommend", methods=["POST"])
@jwt_required()
def send_recommendation_to_farmer():
    """Send a recommendation from Extension Officer to a farmer"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Only extension officers and admins can send recommendations
    if user.role not in ['extension_officer', 'admin']:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json(silent=True) or {}
    farmer_id = data.get("farmer_id")
    message = data.get("message")
    node_id = data.get("node_id")
    
    if not farmer_id or not message or not node_id:
        return jsonify({"error": "farmer_id, node_id and message are required"}), 400
    
    # Check if farmer exists
    farmer = User.query.get(farmer_id)
    if not farmer or farmer.role != 'farmer':
        return jsonify({"error": "Farmer not found"}), 404
    
    # ✅ Check if node exists
    node = SensorNode.query.get(node_id)
    if not node:
        return jsonify({"error": "Node not found"}), 404
    
    # ✅ Check if farmer has selected this node (via FarmerNode OR direct ownership)
    farmer_node = FarmerNode.query.filter_by(
        farmer_id=farmer_id,
        node_id=node_id
    ).first()
    
    if not farmer_node and node.user_id != farmer_id:
        return jsonify({"error": "Node not found or does not belong to farmer"}), 404
    
    # Create alert for the farmer
    alert = Alert(
        node_id=node_id,
        alert_type="RECOMMENDATION",
        message=f"👨‍🏫 Recommendation from {user.username}: {message}",
        severity="INFO"
    )
    db.session.add(alert)
    db.session.commit()
    
    return jsonify({
        "message": "Recommendation sent successfully",
        "alert": alert.to_dict()
    }), 201