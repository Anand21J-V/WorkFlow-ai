from flask import Blueprint, request, jsonify
from services import ai_endpoint

query_bp = Blueprint('query', __name__)

@query_bp.route("/api/query", methods=["POST"])
def query_endpoint():
    try:
        data = request.get_json()
        payload = data.get("payload")
        
        response = ai_endpoint(payload, action="query")
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500