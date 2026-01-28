# from llama_index.vector_stores.supabase import SupabaseVectorStore
# from llama_index.core import VectorStoreIndex, StorageContext
# from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
# from llama_index.core.postprocessor import SentenceTransformerRerank
# from llama_index.core import QueryBundle
# from config import settings

# def retrieve_and_rerank(query: str, user_id: str, doc_id: str, top_k: int = 5) -> str:
#     vector_store = SupabaseVectorStore(
#         postgres_connection_string=settings.POSTGRES_CONNECTION,
#         collection_name="rag_testing",
#         embedding_dimension=1536
#     )
    
#     storage_context = StorageContext.from_defaults(vector_store=vector_store)
#     index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
    
#     filters = MetadataFilters(
#         filters=[
#             ExactMatchFilter(key="user_id", value=user_id),
#             ExactMatchFilter(key="source", value=doc_id)
#         ],
#         condition="and"
#     )
    
#     retriever = index.as_retriever(similarity_top_k=15, filters=filters)
#     top15_nodes = retriever.retrieve(query)
    
#     query_bundle = QueryBundle(query_str=query)
#     reranker = SentenceTransformerRerank(
#         model="cross-encoder/ms-marco-MiniLM-L-6-v2",
#         top_n=top_k
#     )
#     top_k_nodes = reranker.postprocess_nodes(top15_nodes, query_bundle)
    
#     chunks_context = ""
#     for i, node in enumerate(top_k_nodes, 1):
#         text = node.node.text
#         chunks_context += f"CHUNK {i}:\n{text}\n\n"
    
#     return chunks_context






from llama_index.vector_stores.supabase import SupabaseVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core import QueryBundle
from config import settings

from typing import List, Dict

# ------------------------------------------------------------------
# 🔹 EXISTING FUNCTION (UNCHANGED – DO NOT TOUCH)
# ------------------------------------------------------------------

def retrieve_and_rerank(query: str, user_id: str, doc_id: str, top_k: int = 5) -> str:
    vector_store = SupabaseVectorStore(
        postgres_connection_string=settings.POSTGRES_CONNECTION,
        collection_name="rag_testing",
        embedding_dimension=1536
    )
    
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context
    )
    
    filters = MetadataFilters(
        filters=[
            ExactMatchFilter(key="user_id", value=user_id),
            ExactMatchFilter(key="source", value=doc_id)
        ],
        condition="and"
    )
    
    retriever = index.as_retriever(similarity_top_k=15, filters=filters)
    top15_nodes = retriever.retrieve(query)
    
    query_bundle = QueryBundle(query_str=query)
    reranker = SentenceTransformerRerank(
        model="cross-encoder/ms-marco-MiniLM-L-6-v2",
        top_n=top_k
    )
    top_k_nodes = reranker.postprocess_nodes(top15_nodes, query_bundle)
    
    chunks_context = ""
    for i, node in enumerate(top_k_nodes, 1):
        text = node.node.text
        chunks_context += f"CHUNK {i}:\n{text}\n\n"
    
    return chunks_context


# ------------------------------------------------------------------
# 🔹 NEW: MEMORY FUNCTIONS (ADDED, NOTHING REMOVED)
# ------------------------------------------------------------------

# simple in-process memory store
_MEMORY_STORE: Dict[str, List[Dict[str, str]]] = {}


def get_user_memory(user_id: str) -> List[Dict[str, str]]:
    """
    Returns conversation history for a user
    """
    return _MEMORY_STORE.get(user_id, [])


def update_user_memory(
    user_id: str,
    role: str | None = None,
    content: str | None = None,
    message: Dict[str, str] | None = None
) -> None:
    """
    Updates user memory.
    Supports multiple calling styles:
    - update_user_memory(user_id, role, content)
    - update_user_memory(user_id, message={...})
    """

    if user_id not in _MEMORY_STORE:
        _MEMORY_STORE[user_id] = []

    if message is not None:
        # message dict style
        role = message.get("role")
        content = message.get("content")

    if role is None or content is None:
        # silently ignore invalid calls instead of crashing
        return

    _MEMORY_STORE[user_id].append({
        "role": role,
        "content": content
    })



def format_conversation_history(
    memory: List[Dict[str, str]],
    last_n: int | None = None
) -> str:
    """
    Converts memory list into prompt-ready string
    If last_n is provided, only last N messages are used
    """

    if last_n is not None:
        memory = memory[-last_n:]

    return "\n".join(
        f"{m['role'].upper()}: {m['content']}"
        for m in memory
    )
