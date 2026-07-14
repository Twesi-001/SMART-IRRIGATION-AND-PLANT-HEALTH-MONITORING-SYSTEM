from flask import Blueprint, request, jsonify  # type: ignore
from app.extensions import db
from app.models import Prediction, SensorReading
from app.device_auth import require_device_key

predictions_bp = Blueprint("predictions", __name__, url_prefix="/api/predictions")


@predictions_bp.route("", methods=["POST"])
@require_device_key
def submit_prediction():
    """Called by the scikit-learn inference script after it scores
    a new sensor reading."""
    data = request.get_json(silent=True) or {}

    reading_id = data.get("reading_id")
    irrigation_needed = data.get("irrigation_needed")
    recommended_action = data.get("recommended_action")
    confidence = data.get("confidence")
    model_version = data.get("model_version")

    if reading_id is None or irrigation_needed is None or not model_version:
        return jsonify({"error": "reading_id, irrigation_needed and model_version are required"}), 400

    if not SensorReading.query.get(reading_id):
        return jsonify({"error": f"reading_id {reading_id} does not exist"}), 404

    prediction = Prediction(
        reading_id=reading_id,
        irrigation_needed=bool(irrigation_needed),
        recommended_action=recommended_action,
        confidence=confidence,
        model_version=model_version,
    )
    db.session.add(prediction)
    db.session.commit()

    return jsonify(prediction.to_dict()), 201


@predictions_bp.route("/latest", methods=["GET"])
def latest_prediction():
    node_id = request.args.get("node_id", 1, type=int)
    prediction = (
        Prediction.query.join(SensorReading)
        .filter(SensorReading.node_id == node_id)
        .order_by(Prediction.created_at.desc())
        .first()
    )
    if not prediction:
        return jsonify({"error": "no predictions found for this node"}), 404
    return jsonify(prediction.to_dict()), 200


@predictions_bp.route("/history", methods=["GET"])
def prediction_history():
    node_id = request.args.get("node_id", 1, type=int)
    limit = request.args.get("limit", 100, type=int)

    predictions = (
        Prediction.query.join(SensorReading)
        .filter(SensorReading.node_id == node_id)
        .order_by(Prediction.created_at.desc())
        .limit(min(limit, 1000))
        .all()
    )
    return jsonify([p.to_dict() for p in predictions]), 200
@predictions_bp.route("/predict", methods=["POST"])
@require_device_key
def predict_from_sensor():
    """Shortcut endpoint that takes sensor data and returns prediction"""
    data = request.get_json(silent=True) or {}
    
    node_id = data.get("node_id")
    soil_moisture = data.get("soil_moisture")
    temperature = data.get("temperature")
    humidity = data.get("humidity")
    
    if node_id is None or soil_moisture is None:
        return jsonify({"error": "node_id and soil_moisture are required"}), 400
    
    # Get the node's threshold
    from app.models import SensorNode
    node = SensorNode.query.get(node_id)
    if not node:
        return jsonify({"error": f"node_id {node_id} does not exist"}), 404
    
    threshold = float(node.moisture_threshold) if node.moisture_threshold else 30.0
    
    # Simple threshold-based prediction
    irrigation_needed = soil_moisture < threshold
    
    # Calculate confidence based on how far from threshold
    diff = abs(soil_moisture - threshold)
    confidence = min(0.95, 0.5 + (diff / 100))
    
    recommended_action = "Water now" if irrigation_needed else "No irrigation needed"
    
    # Get the latest reading for this node to associate the prediction
    latest_reading = SensorReading.query.filter_by(node_id=node_id)\
                                       .order_by(SensorReading.recorded_at.desc()).first()
    
    if latest_reading:
        prediction = Prediction(
            reading_id=latest_reading.id,
            irrigation_needed=irrigation_needed,
            recommended_action=recommended_action,
            confidence=confidence,
            model_version="simple_threshold_v1"
        )
        db.session.add(prediction)
        db.session.commit()
        
        return jsonify({
            "node_id": node_id,
            "soil_moisture": soil_moisture,
            "threshold": threshold,
            "irrigation_needed": irrigation_needed,
            "recommended_action": recommended_action,
            "confidence": confidence,
            "prediction_id": prediction.id,
            "reading_id": latest_reading.id
        }), 200
    else:
        # If no reading exists, just return prediction without saving
        return jsonify({
            "node_id": node_id,
            "soil_moisture": soil_moisture,
            "threshold": threshold,
            "irrigation_needed": irrigation_needed,
            "recommended_action": recommended_action,
            "confidence": confidence,
            "message": "Prediction not saved (no reading found for this node)"
        }), 200