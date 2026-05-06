from typing import Optional, Literal
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_INDEX: Optional[str] = None
    VECTOR_STORE_TYPE: Literal["faiss", "pinecone"] = "faiss"
    VECTOR_EMBEDDING_TYPE: Literal["openai", "huggingface"] = "huggingface"
    FAISS_INDEX_PATH: str = "./data/faiss_index"
    UPLOAD_DIR: str = "./data/uploads"
    MAX_FILE_SIZE_MB: int = 50
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    LLM_MODEL: str = "llama3-8b-8192"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    SECRET_KEY: str
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:5005", "http://localhost:5006"]

    class Config:
        env_file = ".env"

settings = Settings()
