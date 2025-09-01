"""
Redis-backed implementation of SessionRepository with TTL.
"""
from __future__ import annotations

import json
from datetime import timedelta
from typing import Any, Dict, Optional

from domain.ports.session_repository import SessionRepository
from domain.value_objects.identifiers import SessionId
from infrastructure.redis.client import get_redis_client
from core.config import get_settings


class RedisSessionRepository(SessionRepository):
    def __init__(self) -> None:
        self.settings = get_settings()
        self._redis = get_redis_client(db=self.settings.REDIS_DB_SESSIONS)

    async def get_session_data(self, session_id: SessionId) -> Optional[Dict[str, Any]]:
        if not self._redis:
            return None
        data = await self._redis.get(self._key(session_id.value))  # type: ignore[attr-defined]
        if not data:
            return None
        try:
            return json.loads(data)
        except Exception:
            return None

    async def save_session_data(
        self, session_id: SessionId, data: Dict[str, Any], ttl: Optional[int] = None
    ) -> None:
        if not self._redis:
            return None
        ex = int(ttl) if ttl else None
        payload = json.dumps(data)
        await self._redis.set(self._key(session_id.value), payload, ex=ex)  # type: ignore[attr-defined]
        return None

    async def session_exists(self, session_id: SessionId) -> bool:
        if not self._redis:
            return False
        return bool(await self._redis.exists(self._key(session_id.value)))  # type: ignore[attr-defined]

    async def extend_session_ttl(self, session_id: SessionId, ttl: int) -> None:
        if not self._redis:
            return None
        await self._redis.expire(self._key(session_id.value), int(ttl))  # type: ignore[attr-defined]
        return None

    async def delete_session(self, session_id: SessionId) -> None:
        if not self._redis:
            return None
        await self._redis.delete(self._key(session_id.value))  # type: ignore[attr-defined]
        return None

    @staticmethod
    def _key(session_id: str) -> str:
        return f"session:{session_id}"
