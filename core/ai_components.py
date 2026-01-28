import os
from mem0 import Memory
from langchain_openai import ChatOpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
from supabase import create_client
from config import settings

class AIComponents:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.memory = Memory.from_config(settings.MEM0_CONFIG)
        
        self.llm = ChatOpenAI(
            model="openai/gpt-4o-mini",
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=os.environ["OPENAI_BASE_URL"],
            temperature=0.0
        )
        
        self.embed_model = OpenAIEmbedding(
            api_key=os.environ["OPENAI_API_KEY"],
            model="text-embedding-3-small",
            api_base=os.environ["OPENAI_BASE_URL"]
        )
        
        Settings.embed_model = self.embed_model
        
        self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

ai_components = AIComponents()