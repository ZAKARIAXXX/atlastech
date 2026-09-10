from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "ATLASTECH_", "env_file": ".env", "extra": "ignore"}

    environment: str = "development"
    database_url: str = "postgresql+asyncpg://atlastech:atlastech@localhost:5432/atlastech"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: list[str] = ["http://localhost:3000"]

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    api_key_header: str = "X-API-Key"
    api_key: str = "dev-api-key-change-me"

    @model_validator(mode="after")
    def validate_production_secrets(self) -> Self:
        """Enforce strict secret security in production environments."""
        if self.environment == "production":
            insecure_defaults = [
                "change-me-in-production",
                "dev-api-key-change-me",
                "secret",
                "password",
            ]
            if self.jwt_secret_key in insecure_defaults or len(self.jwt_secret_key) < 32:
                raise ValueError(
                    "FATAL: In production, ATLASTECH_JWT_SECRET_KEY must be set to a secure key (>=32 chars)"
                )
            if self.api_key in insecure_defaults or len(self.api_key) < 16:
                raise ValueError(
                    "FATAL: In production, ATLASTECH_API_KEY must be set to a secure key (>=16 chars)"
                )
        return self


settings = Settings()
