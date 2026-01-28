import json
import psycopg2
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from llama_index.core.schema import Document
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.supabase import SupabaseVectorStore
from llama_index.core.node_parser import SemanticSplitterNodeParser
from core import ai_components
from config import settings

def get_full_document_text(user_id: str, doc_id: str) -> str:
    conn = psycopg2.connect(settings.POSTGRES_CONNECTION)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT metadata->>'_node_content'
        FROM vecs.rag_testing
        WHERE metadata->>'user_id' = %s
          AND metadata->>'source' = %s
        ORDER BY
          (metadata->>'page')::int,
          (metadata->>'chunk_index')::int;
    """, (user_id, doc_id))
    
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    texts = []
    for (node_content_str,) in rows:
        if not node_content_str:
            continue
        node_content = json.loads(node_content_str)
        chunk_text = node_content.get("text", "").strip()
        if chunk_text:
            texts.append(chunk_text)
    
    return "\n\n".join(texts)

SUMMARY_PROMPT = """
You are an educational summarization assistant.

Your task is to create a clear, student-friendly summary of the document below.

INSTRUCTIONS:
- Use ONLY the information from the document.
- Do NOT add external knowledge.
- Capture key points, roles, responsibilities, timelines, and important details.
- Organize the summary in clear paragraphs or bullet points.
- Keep the summary concise but complete.
- Do NOT mention that this is a summary of a document.

DOCUMENT:
{document_text}
"""

def summarize_document(document_text: str) -> str:
    prompt = SUMMARY_PROMPT.format(document_text=document_text)
    response = ai_components.llm.invoke(prompt)
    return response.content

MCQ_PROMPT = """
You are an educational quiz generator.

Based ONLY on the summary below, generate exactly 5 objective (multiple-choice) questions.

RULES:
- Use ONLY the information in the summary.
- Each question must have exactly 4 options.
- Only ONE option must be correct.
- The correct answer must be clearly inferable from the summary.
- Avoid yes/no questions.
- Avoid repeating the same concept.
- Questions should test understanding suitable for students.

Return ONLY valid JSON in the following format:
{{
  "quiz": [
    {{
      "question": "string",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "string"
    }}
  ]
}}

SUMMARY:
{summary_text}
"""

def generate_quiz(user_id: str, doc_id: str) -> Dict[str, Any]:
    full_document_text = get_full_document_text(user_id, doc_id)
    
    if not full_document_text:
        raise ValueError(f"No document found for user_id={user_id}, doc_id={doc_id}")
    
    summary = summarize_document(full_document_text)
    
    prompt = MCQ_PROMPT.format(summary_text=summary)
    response = ai_components.llm.invoke(prompt)
    content = response.content.strip()
    
    try:
        quiz_result = json.loads(content)
        return {
            "questions": quiz_result["quiz"],
            "summary": summary
        }
    except:
        return {
            "questions": [],
            "summary": summary
        }

def ingest_document(file_path: str, user_id: str, doc_id: str) -> Dict[str, Any]:
    loader = PyPDFLoader(file_path)
    langchain_docs = loader.load()
    
    llama_docs = []
    for i, doc in enumerate(langchain_docs):
        llama_doc = Document(
            text=doc.page_content,
            id_=f"pdf-page-{i+1}",
            metadata={
                "page": i+1,
                "source": doc_id,
                "user_id": user_id
            }
        )
        llama_docs.append(llama_doc)
    
    parser = SemanticSplitterNodeParser(
        embed_model=ai_components.embed_model,
        breakpoint_percentile_threshold=85
    )
    
    nodes = parser.get_nodes_from_documents(llama_docs)
    
    nodes_sorted = sorted(
        nodes,
        key=lambda n: (
            n.metadata.get("page", 0),
            n.start_char_idx
        )
    )
    
    for idx, node in enumerate(nodes_sorted):
        node.metadata["chunk_index"] = idx
    
    vector_store = SupabaseVectorStore(
        postgres_connection_string=settings.POSTGRES_CONNECTION,
        collection_name="rag_testing",
        embedding_dimension=1536
    )
    
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    index = VectorStoreIndex(
        nodes_sorted,
        storage_context=storage_context,
        show_progress=False
    )
    
    return {
        "total_pages": len(llama_docs),
        "total_chunks": len(nodes_sorted),
        "chunks_stored": len(nodes_sorted)
    }

def inspect_chunks(user_id: str, doc_id: str) -> List[Dict[str, Any]]:
    conn = psycopg2.connect(settings.POSTGRES_CONNECTION)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT
            metadata->>'page' AS page,
            metadata->>'chunk_index' AS chunk_index,
            metadata->>'_node_content' AS node_content
        FROM vecs.rag_testing
        WHERE metadata->>'user_id' = %s
          AND metadata->>'source' = %s
        ORDER BY (metadata->>'chunk_index')::int;
    """, (user_id, doc_id))
    
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    chunks = []
    for page, chunk_index, node_content_str in rows:
        chunk_info = {
            "page": page,
            "chunk_index": chunk_index,
            "content": ""
        }
        
        if node_content_str:
            node_json = json.loads(node_content_str)
            chunk_info["content"] = node_json.get("text", "").strip()
        
        chunks.append(chunk_info)
    
    return chunks