from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("farmer", "extension_officer", "admin"), default="farmer", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SensorNode(db.Model):
    __tablename__ = "sensor_nodes"

    id = db.Column(db.Integer, primary_key=True)
    node_name = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(120))
    crop_type = db.Column(db.String(80))
    moisture_threshold = db.Column(db.Numeric(5, 2), default=30.00)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  # ← ADD THIS

    readings = db.relationship("SensorReading", backref="node", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "node_name": self.node_name,
            "location": self.location,
            "crop_type": self.crop_type,
            "moisture_threshold": float(self.moisture_threshold) if self.moisture_threshold is not None else None,
            "is_active": self.is_active,
            "user_id": self.user_id, 
        }

class SensorReading(db.Model):
    __tablename__ = "sensor_readings"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey("sensor_nodes.id"), nullable=False)
    soil_moisture = db.Column(db.Numeric(5, 2), nullable=False)
    temperature = db.Column(db.Numeric(5, 2), nullable=False)
    humidity = db.Column(db.Numeric(5, 2), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    predictions = db.relationship("Prediction", backref="reading", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "node_id": self.node_id,
            "soil_moisture": float(self.soil_moisture),
            "temperature": float(self.temperature),
            "humidity": float(self.humidity),
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
        }


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    reading_id = db.Column(db.BigInteger, db.ForeignKey("sensor_readings.id"), nullable=False)
    irrigation_needed = db.Column(db.Boolean, nullable=False)
    recommended_action = db.Column(db.String(120))
    confidence = db.Column(db.Numeric(5, 4))
    model_version = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "reading_id": self.reading_id,
            "irrigation_needed": self.irrigation_needed,
            "recommended_action": self.recommended_action,
            "confidence": float(self.confidence) if self.confidence is not None else None,
            "model_version": self.model_version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PumpCommand(db.Model):
    __tablename__ = "pump_commands"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey("sensor_nodes.id"), nullable=False)
    command = db.Column(db.Enum("ON", "OFF"), nullable=False)
    source = db.Column(db.Enum("AUTO", "MANUAL"), nullable=False)
    issued_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "node_id": self.node_id,
            "command": self.command,
            "source": self.source,
            "issued_by": self.issued_by,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
        }


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey("sensor_nodes.id"), nullable=False)
    alert_type = db.Column(db.String(60), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    severity = db.Column(db.Enum("INFO", "WARNING", "CRITICAL"), default="WARNING")
    resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "node_id": self.node_id,
            "alert_type": self.alert_type,
            "message": self.message,
            "severity": self.severity,
            "resolved": self.resolved,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }
