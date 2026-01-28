from flask import Blueprint, request, jsonify
from services import inspect_chunks

inspect_bp = Blueprint('inspect', __name__)

@inspect_bp.route("/api/inspect", methods=["POST"])
def inspect_endpoint():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        doc_id = data.get("doc_id")
        
        chunks = inspect_chunks(user_id, doc_id)
        return jsonify({
            "user_id": user_id,
            "doc_id": doc_id,
            "total_chunks": len(chunks),
            "chunks": chunks
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500