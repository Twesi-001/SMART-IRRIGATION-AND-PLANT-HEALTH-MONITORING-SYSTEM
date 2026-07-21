from flask import Blueprint, request, jsonify # type: ignore
from flask_jwt_extended import jwt_required, get_jwt_identity # type: ignore
from app.extensions import db
from app.models import PumpCommand, SensorNode, SensorReading
from app.device_auth import require_device_key
from sqlalchemy import desc # type: ignore

pump_bp = Blueprint("pump", __name__, url_prefix="/api/pump")


# ===== HELPER FUNCTION =====
def is_irrigation_needed(node_id):
    """Check if soil moisture is below threshold for a given node"""
    node = SensorNode.query.get(node_id)
    if not node:
        return False, None, None
    
    latest_reading = SensorReading.query.filter_by(node_id=node_id)\
        .order_by(desc(SensorReading.recorded_at)).first()
    
    if not latest_reading:
        return False, None, None
    
    threshold = float(node.moisture_threshold)
    moisture = float(latest_reading.soil_moisture)
    irrigation_needed = moisture < threshold
    
    return irrigation_needed, moisture, threshold


# ===== ENDPOINTS =====

@pump_bp.route("/command", methods=["POST"])
@jwt_required()
def manual_command():
    """A logged-in farmer/extension officer overrides the pump from the dashboard."""
    data = request.get_json(silent=True) or {}
    node_id = data.get("node_id", 1)
    command = data.get("command")

    if command not in ("ON", "OFF"):
        return jsonify({"error": "command must be 'ON' or 'OFF'"}), 400

    if not SensorNode.query.get(node_id):
        return jsonify({"error": f"node_id {node_id} does not exist"}), 404

    # ✅ Check if irrigation is needed BEFORE allowing pump ON
    if command == "ON":
        irrigation_needed, moisture, threshold = is_irrigation_needed(node_id)
        if not irrigation_needed:
            return jsonify({
                "error": "🚫 Irrigation not needed. Soil moisture is above threshold.",
                "status": "LOCKED",
                "soil_moisture": moisture,
                "threshold": threshold,
                "message": f"Soil moisture ({moisture}%) is above threshold ({threshold}%). Pump cannot be turned ON."
            }), 403

    user_id = get_jwt_identity()
    entry = PumpCommand(node_id=node_id, command=command, source="MANUAL", issued_by=user_id)
    db.session.add(entry)
    db.session.commit()

    return jsonify(entry.to_dict()), 201


@pump_bp.route("/auto-command", methods=["POST"])
@require_device_key
def auto_command():
    """Called by the embedded/edge logic when the pump is switched automatically."""
    data = request.get_json(silent=True) or {}
    node_id = data.get("node_id", 1)
    command = data.get("command")

    if command not in ("ON", "OFF"):
        return jsonify({"error": "command must be 'ON' or 'OFF'"}), 400

    if not SensorNode.query.get(node_id):
        return jsonify({"error": f"node_id {node_id} does not exist"}), 404

    # ✅ Auto command respects moisture threshold
    if command == "ON":
        irrigation_needed, moisture, threshold = is_irrigation_needed(node_id)
        if not irrigation_needed:
            return jsonify({
                "error": "🚫 Auto pump OFF - soil moisture is above threshold.",
                "status": "LOCKED",
                "soil_moisture": moisture,
                "threshold": threshold
            }), 403

    entry = PumpCommand(node_id=node_id, command=command, source="AUTO", issued_by=None)
    db.session.add(entry)
    db.session.commit()

    return jsonify(entry.to_dict()), 201


@pump_bp.route("/status", methods=["GET"])
def pump_status():
    node_id = request.args.get("node_id", 1, type=int)
    latest = (PumpCommand.query.filter_by(node_id=node_id)
              .order_by(PumpCommand.issued_at.desc()).first())
    
    if not latest:
        return jsonify({"status": "UNKNOWN", "detail": "no pump commands logged yet"}), 404
    
    # ✅ Check irrigation status
    irrigation_needed, moisture, threshold = is_irrigation_needed(node_id)
    
    return jsonify({
        "status": latest.command,
        "source": latest.source,
        "issued_by": latest.issued_by,
        "issued_at": latest.issued_at.isoformat(),
        "irrigation_needed": irrigation_needed,
        "soil_moisture": moisture,
        "threshold": threshold,
        "can_toggle_on": irrigation_needed,
        "message": "Irrigation needed! Turn pump ON." if irrigation_needed else "Soil moisture is sufficient. Pump is locked OFF."
    }), 200


@pump_bp.route("/history", methods=["GET"])
def pump_history():
    node_id = request.args.get("node_id", 1, type=int)
    limit = request.args.get("limit", 100, type=int)
    commands = (PumpCommand.query.filter_by(node_id=node_id)
                .order_by(PumpCommand.issued_at.desc())
                .limit(min(limit, 1000)).all())
    return jsonify([c.to_dict() for c in commands]), 200


@pump_bp.route("/<int:node_id>/toggle", methods=["POST"])
@jwt_required()
def toggle_pump(node_id):
    """Toggle pump status (ON->OFF or OFF->ON)"""
    if not SensorNode.query.get(node_id):
        return jsonify({"error": f"node_id {node_id} does not exist"}), 404
    
    latest = (PumpCommand.query.filter_by(node_id=node_id)
              .order_by(PumpCommand.issued_at.desc()).first())
    
    current = latest.command if latest else "OFF"
    new_command = "OFF" if current == "ON" else "ON"
    
    # ✅ If trying to turn ON, check if irrigation is needed
    if new_command == "ON":
        irrigation_needed, moisture, threshold = is_irrigation_needed(node_id)
        if not irrigation_needed:
            return jsonify({
                "error": "🚫 Irrigation not needed. Soil moisture is above threshold.",
                "status": "LOCKED",
                "soil_moisture": moisture,
                "threshold": threshold,
                "message": f"Soil moisture ({moisture}%) is above threshold ({threshold}%). Pump cannot be turned ON."
            }), 403
    
    user_id = get_jwt_identity()
    entry = PumpCommand(node_id=node_id, command=new_command, source="MANUAL", issued_by=user_id)
    db.session.add(entry)
    db.session.commit()
    
    return jsonify({
        'node_id': node_id,
        'previous_status': current,
        'new_status': new_command,
        'command_id': entry.id,
        'issued_at': entry.issued_at.isoformat()
    }), 201


@pump_bp.route("/<int:node_id>/status", methods=["GET"])
def get_pump_status_for_node(node_id):
    """Get pump status for a specific node (path parameter version)"""
    if not SensorNode.query.get(node_id):
        return jsonify({"error": f"node_id {node_id} does not exist"}), 404
    
    latest = (PumpCommand.query.filter_by(node_id=node_id)
              .order_by(PumpCommand.issued_at.desc()).first())
    
    # ✅ Check irrigation status
    irrigation_needed, moisture, threshold = is_irrigation_needed(node_id)
    
    if not latest:
        return jsonify({
            'node_id': node_id,
            'status': 'UNKNOWN',
            'message': 'No pump commands logged yet',
            'irrigation_needed': irrigation_needed,
            'soil_moisture': moisture,
            'threshold': threshold,
            'can_toggle_on': irrigation_needed
        }), 200
    
    return jsonify({
        'node_id': node_id,
        'status': latest.command,
        'last_changed': latest.issued_at.isoformat(),
        'source': latest.source,
        'issued_by': latest.issued_by,
        'irrigation_needed': irrigation_needed,
        'soil_moisture': moisture,
        'threshold': threshold,
        'can_toggle_on': irrigation_needed,
        'message': "Irrigation needed!" if irrigation_needed else "Soil moisture OK. Pump locked OFF."
    }), 200