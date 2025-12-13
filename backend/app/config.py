"""
Application configuration management using pydantic-settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        env="OPENAI_EMBEDDING_MODEL"
    )

    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")

    # Qdrant Configuration
    qdrant_url: str = Field(..., env="QDRANT_URL")
    qdrant_api_key: str = Field(..., env="QDRANT_API_KEY")
    qdrant_collection_name: str = Field(
        default="physical_ai_textbook",
        env="QDRANT_COLLECTION_NAME"
    )

    # Authentication
    auth_secret: str = Field(..., env="AUTH_SECRET")
    auth_url: str = Field(default="http://localhost:3000", env="AUTH_URL")

    # API Configuration
    backend_url: str = Field(default="http://localhost:8000", env="BACKEND_URL")
    cors_origins: str = Field(
        default="http://localhost:3000",
        env="CORS_ORIGINS"
    )

    # Environment
    environment: str = Field(default="development", env="PYTHON_ENV")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
