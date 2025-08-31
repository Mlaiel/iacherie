"""Simple API key auth dependency for service-to-service protection."""from typing import Optional
from fastapi import Header, HTTPException, status, Depends

from .config import settings


async def api_key_auth(x_api_key: Optional[str] = Header(None)) -> str:
    if not settings.api_keys:
        return "anonymous"
    if x_api_key in settings.api_keys:
        return "service"
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
