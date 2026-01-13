"""Application configuration"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    # Salt API Configuration
    SALT_API_URL: str = "http://localhost:8000"
    SALT_API_USER: str = "saltapi"
    SALT_API_PASSWORD: str = "saltapi"

    # Application Configuration
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    SECRET_KEY: str = "dev_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()
