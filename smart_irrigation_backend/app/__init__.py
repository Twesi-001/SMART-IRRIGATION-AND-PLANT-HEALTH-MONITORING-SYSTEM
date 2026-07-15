from flask import Flask, jsonify # type: ignore
from flask_cors import CORS # type: ignore

from app.config import Config
from app.extensions import db, jwt
from app.dashboard import dashboard_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    
    # ✅ Updated CORS configuration with production frontend URL
    CORS(app, supports_credentials=True, origins=[
        "http://localhost:3000",  # Local development
        "http://127.0.0.1:3000",  # Local development alternative
        "https://smart-irrigation-and-plant-health-m.vercel.app"  # ← YOUR DEPLOYED FRONTEND URL
    ])

    from app.auth import auth_bp
    from app.readings import readings_bp
    from app.predictions import predictions_bp
    from app.pump import pump_bp
    from app.alerts import alerts_bp
    from app.nodes import nodes_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(readings_bp)
    app.register_blueprint(predictions_bp)
    app.register_blueprint(pump_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(nodes_bp)
    app.register_blueprint(dashboard_bp)

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "internal server error"}), 500

    return app