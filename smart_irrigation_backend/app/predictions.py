from flask import Blueprint, request, jsonify  # type: ignore
from app.extensions import db
from app.models import Prediction, SensorReading, SensorNode
from app.device_auth import require_device_key
import joblib # type: ignore
import os
import numpy as np # type: ignore

predictions_bp = Blueprint("predictions", __name__, url_prefix="/api/predictions")

# Load the trained ML model
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'irrigation_model_all_crops.pkl')
try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ ML model loaded from: {MODEL_PATH}")
except Exception as e:
    model = None
    print(f"❌ Failed to load ML model: {e}")


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
    """
    ML-powered prediction endpoint using the trained Random Forest model.
    Takes sensor data and node_id, returns irrigation prediction.
    """
    data = request.get_json(silent=True) or {}
    
    node_id = data.get("node_id")
    soil_moisture = data.get("soil_moisture")
    temperature = data.get("temperature")
    humidity = data.get("humidity")
    
    if node_id is None or soil_moisture is None:
        return jsonify({"error": "node_id and soil_moisture are required"}), 400
    
    # Check if node exists
    node = SensorNode.query.get(node_id)
    if not node:
        return jsonify({"error": f"node_id {node_id} does not exist"}), 404
    
    # If ML model is not available, fall back to threshold-based
    if model is None:
        threshold = float(node.moisture_threshold) if node.moisture_threshold else 30.0
        irrigation_needed = soil_moisture < threshold
        diff = abs(soil_moisture - threshold)
        confidence = min(0.95, 0.5 + (diff / 100))
        recommended_action = "Water now" if irrigation_needed else "No irrigation needed"
        model_version = "fallback_threshold"
        
    else:
        # Use ML model
        try:
            features = np.array([[soil_moisture, temperature, humidity, node_id]])
            prediction = model.predict(features)[0]
            confidence = float(max(model.predict_proba(features)[0]))
            irrigation_needed = bool(prediction)
            recommended_action = "Water now" if irrigation_needed else "No irrigation needed"
            model_version = "random_forest_v2"
        except Exception as e:
            return jsonify({"error": f"ML prediction failed: {str(e)}"}), 500
    
    # Get the latest reading for this node to associate the prediction
    latest_reading = SensorReading.query.filter_by(node_id=node_id)\
                                       .order_by(SensorReading.recorded_at.desc()).first()
    
    if latest_reading:
        prediction_record = Prediction(
            reading_id=latest_reading.id,
            irrigation_needed=irrigation_needed,
            recommended_action=recommended_action,
            confidence=confidence,
            model_version=model_version
        )
        db.session.add(prediction_record)
        db.session.commit()
        
        return jsonify({
            "node_id": node_id,
            "soil_moisture": soil_moisture,
            "temperature": temperature,
            "humidity": humidity,
            "irrigation_needed": irrigation_needed,
            "recommended_action": recommended_action,
            "confidence": confidence,
            "model_version": model_version,
            "prediction_id": prediction_record.id,
            "reading_id": latest_reading.id
        }), 200
    else:
        return jsonify({
            "node_id": node_id,
            "soil_moisture": soil_moisture,
            "temperature": temperature,
            "humidity": humidity,
            "irrigation_needed": irrigation_needed,
            "recommended_action": recommended_action,
            "confidence": confidence,
            "model_version": model_version,
            "message": "Prediction not saved (no reading found for this node)"
        }), 200