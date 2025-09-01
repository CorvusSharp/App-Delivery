"""
Redis async client helpers.
"""
from __future__ import annotations

from typing import Optional
from redis import asyncio as aioredis

from core.config import get_settings


def get_redis_client(db: Optional[int] = None) -> Optional[aioredis.Redis]:
    """Return aioredis client or None if REDIS_URL not configured."""
    settings = get_settings()
    if not settings.REDIS_URL:
        return None
    url = settings.REDIS_URL
    if db is not None:
        # Override DB index by rewriting last path segment
        # redis://host:port/<db>
        if "/" in url:
            base = url.rsplit("/", 1)[0]
            url = f"{base}/{db}"
        else:
            url = f"{url}/{db}"
    return aioredis.from_url(url, encoding="utf-8", decode_responses=True)
