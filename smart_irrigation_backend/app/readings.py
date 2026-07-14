from datetime import datetime
from flask import Blueprint, request, jsonify  # type: ignore
from app.extensions import db
from app.models import SensorReading, SensorNode
from app.device_auth import require_device_key

readings_bp = Blueprint("readings", __name__, url_prefix="/api/readings")


@readings_bp.route("", methods=["POST"])
@require_device_key
def ingest_reading():
    """Called by the host-side pyserial script each time it reads a
    structured line from the Arduino over USB."""
    data = request.get_json(silent=True) or {}

    node_id = data.get("node_id", 1)
    soil_moisture = data.get("soil_moisture")
    temperature = data.get("temperature")
    humidity = data.get("humidity")

    if soil_moisture is None or temperature is None or humidity is None:
        return jsonify({"error": "soil_moisture, temperature and humidity are required"}), 400

    if not SensorNode.query.get(node_id):
        return jsonify({"error": f"node_id {node_id} does not exist"}), 404

    reading = SensorReading(
        node_id=node_id,
        soil_moisture=soil_moisture,
        temperature=temperature,
        humidity=humidity,
        recorded_at=datetime.utcnow(),
    )
    db.session.add(reading)
    db.session.commit()

    return jsonify(reading.to_dict()), 201


@readings_bp.route("/live", methods=["GET"])
def live_reading():
    node_id = request.args.get("node_id", 1, type=int)
    reading = (
        SensorReading.query.filter_by(node_id=node_id)
        .order_by(SensorReading.recorded_at.desc())
        .first()
    )
    if not reading:
        return jsonify({"error": "no readings found for this node"}), 404
    return jsonify(reading.to_dict()), 200


@readings_bp.route("/history", methods=["GET"])
def reading_history():
    node_id = request.args.get("node_id", 1, type=int)
    limit = request.args.get("limit", 100, type=int)
    start = request.args.get("start")  # ISO format e.g. 2026-07-01T00:00:00
    end = request.args.get("end")

    query = SensorReading.query.filter_by(node_id=node_id)

    if start:
        query = query.filter(SensorReading.recorded_at >= start)
    if end:
        query = query.filter(SensorReading.recorded_at <= end)

    readings = query.order_by(SensorReading.recorded_at.desc()).limit(min(limit, 1000)).all()
    return jsonify([r.to_dict() for r in readings]), 200


# ========== NEW ENDPOINTS ==========

@readings_bp.route("/<int:reading_id>", methods=["GET"])
def get_reading(reading_id):
    """Get a specific reading by ID"""
    reading = SensorReading.query.get(reading_id)
    if not reading:
        return jsonify({"error": "reading not found"}), 404
    return jsonify(reading.to_dict()), 200


@readings_bp.route("/stats/<int:node_id>", methods=["GET"])
def get_reading_stats(node_id):
    """Get min, max, avg readings for a node"""
    from sqlalchemy import func # type: ignore
    
    # Check if node exists
    if not SensorNode.query.get(node_id):
        return jsonify({"error": f"node_id {node_id} does not exist"}), 404
    
    stats = db.session.query(
        func.avg(SensorReading.soil_moisture).label('avg_moisture'),
        func.max(SensorReading.soil_moisture).label('max_moisture'),
        func.min(SensorReading.soil_moisture).label('min_moisture'),
        func.avg(SensorReading.temperature).label('avg_temperature'),
        func.max(SensorReading.temperature).label('max_temperature'),
        func.min(SensorReading.temperature).label('min_temperature'),
        func.avg(SensorReading.humidity).label('avg_humidity'),
        func.max(SensorReading.humidity).label('max_humidity'),
        func.min(SensorReading.humidity).label('min_humidity'),
        func.count(SensorReading.id).label('total_readings')
    ).filter_by(node_id=node_id).first()
    
    return jsonify({
        'node_id': node_id,
        'avg_soil_moisture': float(stats.avg_moisture or 0),
        'max_soil_moisture': float(stats.max_moisture or 0),
        'min_soil_moisture': float(stats.min_moisture or 0),
        'avg_temperature': float(stats.avg_temperature or 0),
        'max_temperature': float(stats.max_temperature or 0),
        'min_temperature': float(stats.min_temperature or 0),
        'avg_humidity': float(stats.avg_humidity or 0),
        'max_humidity': float(stats.max_humidity or 0),
        'min_humidity': float(stats.min_humidity or 0),
        'total_readings': stats.total_readings or 0
    }), 200


@readings_bp.route("/latest/<int:node_id>", methods=["GET"])
def get_latest_reading_for_node(node_id):
    """Get the latest reading for a specific node"""
    reading = SensorReading.query.filter_by(node_id=node_id)\
                                 .order_by(SensorReading.recorded_at.desc())\
                                 .first()
    if not reading:
        return jsonify({"error": f"no readings found for node {node_id}"}), 404
    return jsonify(reading.to_dict()), 200