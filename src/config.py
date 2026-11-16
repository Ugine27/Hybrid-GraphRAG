import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
    
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
    
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
    MAX_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", "10"))

config = Config()
