from flask import Blueprint, jsonify
from core import ai_components

memory_bp = Blueprint('memory', __name__)

@memory_bp.route("/api/memory/<user_id>", methods=["GET"])
def get_memory(user_id):
    try:
        memories = ai_components.memory.get_all(user_id=user_id)

        if not memories:
            return jsonify({
                "user_id": user_id,
                "total_memories": 0,
                "message": "No memory found for this user yet.",
                "memories": []
            }), 200

        formatted_memories = []

        for idx, m in enumerate(memories, 1):
            if isinstance(m, str):
                formatted_memories.append({
                    "id": idx,
                    "content": m
                })
            elif isinstance(m, dict) and "memory" in m:
                formatted_memories.append({
                    "id": idx,
                    "content": m["memory"]
                })

        return jsonify({
            "user_id": user_id,
            "total_memories": len(formatted_memories),
            "message": "Memory successfully retrieved from database.",
            "memories": formatted_memories
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500