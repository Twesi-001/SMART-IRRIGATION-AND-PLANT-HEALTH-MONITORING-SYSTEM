from functools import wraps
from flask import request, jsonify, current_app # type: ignore


def require_device_key(fn):
    """Protects ingest endpoints called by the pyserial data-logging
    script, using a shared secret instead of a full user JWT."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        supplied = request.headers.get("X-API-Key")
        expected = current_app.config.get("INGEST_API_KEY")
        if not supplied or supplied != expected:
            return jsonify({"error": "invalid or missing device API key"}), 401
        return fn(*args, **kwargs)

    return wrapper
