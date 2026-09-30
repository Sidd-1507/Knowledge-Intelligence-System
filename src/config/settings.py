import os
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    
    # OpenAI
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL")
    openai_embedding_model: str = Field(default="text-embedding-3-small", env="OPENAI_EMBEDDING_MODEL")
    
    # AWS S3
    aws_access_key_id: str = Field(..., env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    s3_bucket_name: str = Field(default="knowledge-intelligence-system", env="S3_BUCKET_NAME")
    
    # ChromaDB
    chroma_persist_dir: str = Field(default="./chroma_db", env="CHROMA_PERSIST_DIR")
    chroma_collection_name: str = Field(default="knowledge_base", env="CHROMA_COLLECTION_NAME")
    
    # Application
    flask_host: str = Field(default="0.0.0.0", env="FLASK_HOST")
    flask_port: int = Field(default=5000, env="FLASK_PORT")
    flask_debug: bool = Field(default=True, env="FLASK_DEBUG")
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    max_upload_size_mb: int = Field(default=50, env="MAX_UPLOAD_SIZE_MB")
    
    # Mem0
    mem0_api_key: str = Field(default="", env="MEM0_API_KEY")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
