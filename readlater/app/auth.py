from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from app.config import settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(key: str | None = Security(_api_key_header)):
    if not settings.api_key:
        return  # auth disabled in dev mode
    if key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
