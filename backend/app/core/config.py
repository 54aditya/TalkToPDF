import os
from typing import Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Voice Research Assistant"
    ENV: str = "development"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Databases
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "voice_rag_db"
    QDRANT_URL: str = "http://localhost:6333"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Generative AI
    GEMINI_API_KEY: str

    # Speech Services
    STT_MODEL_NAME: str = "base"
    TTS_PROVIDER: str = "piper"  # 'piper' or 'elevenlabs'
    ELEVENLABS_API_KEY: Optional[str] = None
    ELEVENLABS_VOICE_ID: Optional[str] = "21m00Tcm4TlvDq8ikWAM"

    # Storage
    UPLOAD_DIR: str = "uploads"

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("UPLOAD_DIR")
    @classmethod
    def create_upload_dir(cls, v: str) -> str:
        # Create directories if they do not exist locally
        if not os.path.isabs(v):
            project_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(__file__))
            )
            v = os.path.join(project_dir, v)
        os.makedirs(v, exist_ok=True)
        return v


settings = Settings()
