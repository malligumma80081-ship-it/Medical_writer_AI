from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Medical Writing AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    

    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "sqlite:///./data/medical_writing.db"

    REDIS_URL: str = "redis://redis:6379/0"

    CHROMA_PERSIST_DIRECTORY: str = "data/chroma"

    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3.2"

    # JWT Authentication

    jwt_secret_key: str = "CHANGE_THIS_SECRET"

    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = 15

    refresh_token_expire_days: int = 7

    # Security

    secret_key: str = "CHANGE_THIS_IN_PRODUCTION"

    jwt_secret_key: str = "CHANGE_THIS_SECRET"

    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = 15

    refresh_token_expire_days: int = 7
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()