from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Pinecone is the only external API used by this version.
    pinecone_api_key: str
    pinecone_index_name: str = "agentic-ai-ebook-free"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"

    # Local embedding model. Dimension = 384.
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # Local LLM served by Ollama.
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    top_k: int = 5
    min_relevance_score: float = 0.25
    chunk_size: int = 900
    chunk_overlap: int = 150

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
