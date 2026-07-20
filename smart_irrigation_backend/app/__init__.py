from flask import Flask, jsonify # type: ignore
from flask_cors import CORS # type: ignore

from app.config import Config
from app.extensions import db, jwt
from app.dashboard import dashboard_bp
from app.users import users_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    
    # ✅ CORS configuration - Allow all origins for API routes
    # This allows any frontend (including Vercel preview deployments) to access the API
    CORS(app, 
         resources={r"/api/*": {"origins": "*"}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization", "X-API-Key"],
         methods=["GET", "PUT", "POST", "DELETE", "OPTIONS"]
    )

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
    app.register_blueprint(users_bp)

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