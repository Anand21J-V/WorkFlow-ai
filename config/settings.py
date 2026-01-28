import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

POSTGRES_CONNECTION = os.getenv("POSTGRES_CONNECTION")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

SUPABASE_STORAGE_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlkZWp6ZWF5cHhqYWlkeW1xeGhlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTA2NDkxOSwiZXhwIjoyMDg0NjQwOTE5fQ.MpkyziTKjBDgitWdDfLbDC-qR5kRCAuphjjrp57PNs0"

MEM0_CONFIG = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "openai/gpt-4o-mini"
        }
    },
    "vector_store": {
        "provider": "supabase",
        "config": {
            "connection_string": POSTGRES_CONNECTION,
            "collection_name": "memories",
            "embedding_model_dims": 1536
        }
    }
}