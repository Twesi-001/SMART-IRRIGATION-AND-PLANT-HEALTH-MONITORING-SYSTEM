from datetime import datetime
from flask import Blueprint, request, jsonify # type: ignore
from flask_jwt_extended import jwt_required # type: ignore
from app.extensions import db
from app.models import Alert, SensorNode
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
    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({"error": "alert not found"}), 404

    alert.resolved = True
    alert.resolved_at = datetime.utcnow()
    db.session.commit()

    return jsonify(alert.to_dict()), 200


@alerts_bp.route("/<int:alert_id>", methods=["GET"])
@jwt_required()
def get_alert(alert_id):
    """Get a specific alert by ID"""
    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({"error": "alert not found"}), 404
    return jsonify(alert.to_dict()), 200


@alerts_bp.route("/<int:alert_id>", methods=["DELETE"])
@jwt_required()
def delete_alert(alert_id):
    """Delete an alert (permanent removal)"""
    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({"error": "alert not found"}), 404
    
    db.session.delete(alert)
    db.session.commit()
    return jsonify({"message": f"alert {alert_id} deleted successfully"}), 200


@alerts_bp.route("/resolve-all", methods=["POST"])
@jwt_required()
def resolve_all_alerts():
    """Resolve all alerts for a node"""
    node_id = request.args.get("node_id", 1, type=int)
    
    if not SensorNode.query.get(node_id):
        return jsonify({"error": f"node_id {node_id} does not exist"}), 404
    
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
    """Get all unresolved alerts (across all nodes)"""
    node_id = request.args.get("node_id", type=int)
    
    query = Alert.query.filter_by(resolved=False)
    if node_id:
        query = query.filter_by(node_id=node_id)
    
    alerts = query.order_by(Alert.created_at.desc()).all()
    return jsonify([a.to_dict() for a in alerts]), 200


@alerts_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_alerts_summary():
    """Get summary of alerts (counts by node)"""
    from sqlalchemy import func # type: ignore
    
    summary = db.session.query(
        Alert.node_id,
        func.count(Alert.id).label('unresolved_count')
    ).filter_by(resolved=False).group_by(Alert.node_id).all()
    
    total_unresolved = Alert.query.filter_by(resolved=False).count()
    
    return jsonify({
        'total_unresolved': total_unresolved,
        'by_node': [{'node_id': s.node_id, 'count': s.unresolved_count} for s in summary]
    }), 200