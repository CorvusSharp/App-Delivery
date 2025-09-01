"""
Cached provider wrapper around CBRCurrencyRatesProvider using Redis with TTL.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from loguru import logger

from domain.ports.currency_rates_provider import CurrencyRatesProvider
from domain.value_objects.currency import Currency, Rate
from infrastructure.external.cbr_provider import CBRCurrencyRatesProvider
from infrastructure.redis.client import get_redis_client
from core.config import get_settings


class CachedCurrencyRatesProvider(CurrencyRatesProvider):
    """Redis-cached wrapper for currency rates."""

    KEY_USD_RUB = "rates:USD_RUB"

    def __init__(self, ttl_seconds: int = 600):
        self.ttl = ttl_seconds
        self.settings = get_settings()
        self._fallback = CBRCurrencyRatesProvider()

    async def __aenter__(self):
        await self._fallback.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._fallback.__aexit__(exc_type, exc, tb)

    async def get_usd_to_rub_rate(self) -> Optional[Rate]:
        return await self.get_rate(Currency.usd(), Currency.rub())

    async def get_rate(self, from_currency: Currency, to_currency: Currency) -> Optional[Rate]:
        if from_currency.code != Currency.USD or to_currency.code != Currency.RUB:
            return None

        redis = get_redis_client(db=self.settings.REDIS_DB_CACHE)
        if redis:
            try:
                data = await redis.get(self.KEY_USD_RUB)
            except Exception as e:
                logger.warning(f"Redis GET failed: {e}")
                data = None
            if data:
                try:
                    payload = json.loads(data)
                    value = Decimal(payload["value"])  # stored as string
                    updated_at = (
                        datetime.fromisoformat(payload["updated_at"]).astimezone(timezone.utc)
                        if payload.get("updated_at")
                        else None
                    )
                    return Rate.usd_to_rub(value, updated_at=updated_at)
                except Exception as e:
                    logger.warning(f"Failed to parse cached rate: {e}")

        # Fallback to real provider
        rate = await self._fallback.get_usd_to_rub_rate()
        if rate and redis:
            try:
                payload = {
                    "value": str(rate.value),
                    "updated_at": rate.updated_at.isoformat() if rate.updated_at else None,
                }
                await redis.set(self.KEY_USD_RUB, json.dumps(payload), ex=self.ttl)
            except Exception as e:
                logger.warning(f"Redis SET failed: {e}")
        return rate

    async def is_rate_available(self, from_currency: Currency, to_currency: Currency) -> bool:
        return from_currency.code == Currency.USD and to_currency.code == Currency.RUB
