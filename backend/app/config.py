from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "DocuMind"
    debug: bool = False
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_bucket: str = "documind-uploads"
    aws_region: str = "us-east-1"

    openai_api_key: str
    openai_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"

    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chunk_size: int = 512
    chunk_overlap: int = 64
    retrieval_k: int = 6

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
