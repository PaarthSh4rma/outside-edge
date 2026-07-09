from hmac import compare_digest

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import settings


admin_api_key_header = APIKeyHeader(name="X-Admin-API-Key", auto_error=False)


def require_admin_api_key(api_key: str | None = Security(admin_api_key_header)) -> None:
    if not api_key or not compare_digest(api_key, settings.admin_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin API key.",
        )
