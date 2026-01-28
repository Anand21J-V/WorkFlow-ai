import os
import tempfile
import requests
from flask import Blueprint, request, jsonify
from services import ingest_document
from config import settings

ingest_bp = Blueprint('ingest', __name__)

@ingest_bp.route("/api/ingest", methods=["POST"])
def ingest_endpoint():
    try:
        data = request.get_json()
        
        user_id = data.get("user_id")
        file_name = data.get("file_name")
        file_type = data.get("file_type")
        storage_path = data.get("storage_path")
        document_id = data.get("document_id")
        chat_id = data.get("chat_id")
        
        if not file_name.endswith('.pdf'):
            return jsonify({"error": "Only PDF files are supported"}), 400
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        try:
            response = requests.get(
                storage_path,
                headers={
                    "Authorization": settings.SUPABASE_STORAGE_TOKEN,
                    "Content-Type": "application/pdf"
                },
                stream=True,
                timeout=60
            )

            response.raise_for_status()
            
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file.close()
            
            stats = ingest_document(
                file_path=temp_file.name,
                user_id=user_id,
                doc_id=document_id
            )
            
            return jsonify({
                "status": "success",
                "message": f"Document '{file_name}' fetched from Supabase Storage and ingested successfully",
                "user_id": user_id,
                "doc_id": document_id,
                "total_pages": stats["total_pages"],
                "total_chunks": stats["total_chunks"],
                "chunks_stored": stats["chunks_stored"]
            }), 200
        
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Failed to download document from Supabase Storage: {str(e)}"}), 500
        except Exception as e:
            return jsonify({"error": f"Ingestion failed: {str(e)}"}), 500
        
        finally:
            try:
                os.unlink(temp_file.name)
            except:
                pass
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500