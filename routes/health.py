from flask import Blueprint, jsonify
from datetime import datetime

health_bp = Blueprint('health', __name__)

@health_bp.route("/", methods=["GET"])
def root():
    return jsonify({"status": "running"}), 200

@health_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "llm": "initialized",
            "embeddings": "initialized",
            "memory": "initialized",
            "vector_store": "initialized"
        }
    }), 200