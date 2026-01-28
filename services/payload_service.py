from typing import Dict, Any

def normalize_backend_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        user_id = payload.get("user_id")
        if not user_id:
            raise ValueError("Missing required field: user_id")

        chat_id = payload.get("session_id")
        if not chat_id:
            raise ValueError("Missing required field: session_id")

        query = payload.get("query")
        if not query:
            raise ValueError("Missing required field: query")

        document = payload.get("document", {})
        doc_id = document.get("doc_id")
        if not doc_id:
            raise ValueError("Missing required field: document.doc_id")

        chat_history = payload.get("chat_history", [])

        normalized_history = []
        for msg in chat_history:
            content_obj = msg.get("content", {})
            text = content_obj.get("text", "") if isinstance(content_obj, dict) else str(content_obj)

            if text:
                normalized_history.append({
                    "role": msg.get("role", "user"),
                    "content": text
                })

        return {
            "user_id": str(user_id),
            "chat_id": str(chat_id),
            "doc_id": str(doc_id),
            "query": query,
            "conversation_history": normalized_history
        }

    except Exception as e:
        raise ValueError(f"Failed to normalize backend payload: {str(e)}")