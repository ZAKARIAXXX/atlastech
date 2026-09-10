from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "ATLASTECH_", "env_file": ".env"}

    environment: str = "development"
    database_url: str = "postgresql+asyncpg://atlastech:atlastech@localhost:5432/atlastech"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: list[str] = ["http://localhost:3000"]

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    api_key_header: str = "X-API-Key"
    api_key: str = "dev-api-key-change-me"


settings = Settings()
