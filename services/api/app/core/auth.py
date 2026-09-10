import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

api_key_header_scheme = APIKeyHeader(
    name=settings.api_key_header,
    auto_error=False,
)


async def verify_api_key(
    api_key_header: str | None = Security(api_key_header_scheme),
) -> str:
    """
    Validates the X-API-Key header against the configured API key
    using constant-time comparison to prevent timing attacks.
    """
    if not api_key_header:
        # In development mode, allow easy access if no key header was provided
        if settings.environment == "development":
            return "dev-unauthenticated"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing required API key header",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not secrets.compare_digest(api_key_header, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return api_key_header
