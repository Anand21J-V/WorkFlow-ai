from typing import Dict, Any
from services.payload_service import normalize_backend_payload
from services.retrieval_service import retrieve_and_rerank
from services.memory_service import get_user_memory, format_conversation_history, update_user_memory
from services.router_service import router_agent
from services.content_service import content_agent_text_only, content_agent_text_plus_mindmap
from services.document_service import generate_quiz

def ai_endpoint(payload: Dict[str, Any], action: str = "query") -> Dict[str, Any]:
    try:
        ai_input = normalize_backend_payload(payload)
        
        if action == "quiz":
            quiz_data = generate_quiz(ai_input["user_id"], ai_input["doc_id"])
            
            return {
                "response_type": "TEXT_ONLY",
                "text": "Quiz generated successfully.",
                "mindmap": None,
                "quiz": quiz_data,
                "memory_suggestions": [f"User requested quiz on document {ai_input['doc_id']}"]
            }
        
        elif action == "query":
            rag_context = retrieve_and_rerank(
                query=ai_input["query"],
                user_id=ai_input["user_id"],
                doc_id=ai_input["doc_id"],
                top_k=5
            )
            
            memory_context = get_user_memory(ai_input["user_id"])
            
            conversation_history = format_conversation_history(
                ai_input["conversation_history"],
                last_n=10
            )
            
            state = {
                "query": ai_input["query"],
                "user_id": ai_input["user_id"],
                "chat_id": ai_input["chat_id"],
                "doc_id": ai_input["doc_id"],
                "rag_context": rag_context,
                "memory_context": memory_context,
                "conversation_history": conversation_history,
                "response_mode": "TEXT_ONLY",
                "content": "",
                "mindmap": None
            }
            
            response_mode = router_agent(state)
            state["response_mode"] = response_mode
            
            if response_mode == "TEXT_ONLY":
                output = content_agent_text_only(state)
            else:
                output = content_agent_text_plus_mindmap(state)
            
            update_user_memory(ai_input["user_id"], ai_input["query"])
            
            return {
                "response_type": response_mode,
                "text": output["content"],
                "mindmap": output["mindmap"],
                "quiz": None,
                "memory_suggestions": [
                    f"User asked about: {ai_input['query'][:50]}..."
                ]
            }
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    except Exception as e:
        return {
            "response_type": "TEXT_ONLY",
            "text": f"Error processing request: {str(e)}",
            "mindmap": None,
            "quiz": None,
            "memory_suggestions": []
        }