"""
Роутер для проверки здоровья сервиса.
"""
import time
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import text

from presentation.schemas.health_schemas import HealthCheckResponse
from infrastructure.sqlalchemy.database import AsyncSessionLocal
from infrastructure.external.cbr_provider import CBRCurrencyRatesProvider

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Проверка здоровья сервиса",
    description="Возвращает статус всех компонентов системы"
)
async def health_check():
    """Проверить здоровье всех компонентов системы."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    checks = {}
    overall_status = "healthy"

    # Проверка базы данных
    db_status, db_time = await _measure_component(_check_database)
    checks["database"] = {
        "status": db_status,
        "response_time": f"{db_time:.3f}s"
    }
    if db_status != "healthy":
        overall_status = "unhealthy"

    # Проверка CBR API
    cbr_status, cbr_time = await _measure_component(_check_cbr_api)
    checks["cbr_api"] = {
        "status": cbr_status,
        "response_time": f"{cbr_time:.3f}s"
    }
    if cbr_status != "healthy" and overall_status == "healthy":
        overall_status = "degraded"

    return HealthCheckResponse(
        status=overall_status,
        version="1.0.0",
        timestamp=timestamp,
        checks=checks
    )


async def _measure_component(check_func):
    """Общий хелпер для проверки компонента с измерением времени."""
    start_time = time.time()
    try:
        status = await check_func()
    except Exception:
        status = "unhealthy"
    return status, time.time() - start_time


async def _check_database() -> str:
    """Проверить здоровье базы данных."""
    async with AsyncSessionLocal() as session:
        await session.execute(text("SELECT 1"))
    return "healthy"


async def _check_cbr_api() -> str:
    """Проверить доступность CBR API."""
    cbr_provider = CBRCurrencyRatesProvider()
    async with cbr_provider:
        rate = await cbr_provider.get_usd_to_rub_rate()
    return "healthy" if rate else "degraded"


@router.get(
    "/ping",
    summary="Простая проверка доступности",
    description="Быстрая проверка что сервис отвечает"
)
async def ping():
    """Простая проверка доступности."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"}
