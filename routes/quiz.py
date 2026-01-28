from flask import Blueprint, request, jsonify
from services import ai_endpoint

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route("/api/quiz", methods=["POST"])
def quiz_endpoint():
    try:
        data = request.get_json()
        payload = data.get("payload")
        payload["query"] = "__quiz_generation__"

        response = ai_endpoint(payload, action="quiz")
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500