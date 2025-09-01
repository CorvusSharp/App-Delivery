"""
Роутер для работы с доставкой и периодическими задачами.
"""
from fastapi import APIRouter, Depends, HTTPException

from presentation.schemas.delivery_schemas import (
    TriggerCalculationRequest,
    TriggerCalculationResponse,
    ExchangeRateResponse
)
from presentation.schemas.error_schemas import ErrorResponse
from infrastructure.tasks.delivery_tasks import calculate_delivery_prices
from domain.ports.currency_rates_provider import CurrencyRatesProvider
from infrastructure.tasks.currency_tasks import update_currency_rates
from presentation.dependencies.container import di_container
from infrastructure.external.cached_provider import CachedCurrencyRatesProvider

router = APIRouter()

# TODO: Dependency Injection будет настроен в bootstrap
def get_currency_provider() -> CurrencyRatesProvider:
    # Возьмем провайдера из DI (может быть кэшированным)
    return di_container.get_currency_rates_provider()


@router.post(
    "/delivery/calculate",
    response_model=TriggerCalculationResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Ошибка валидации"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    },
    summary="Запустить расчет цен доставки",
    description="Принудительно запускает расчет стоимости доставки для посылок без цены"
)
async def trigger_calculation(
    request: TriggerCalculationRequest = TriggerCalculationRequest(),
):
    """Запустить расчет стоимости доставки."""
    try:
        # Публикуем bulk-задачу в отдельную очередь (админская операция)
        task = calculate_delivery_prices.apply_async(
            args=[request.limit], queue="pricing-bulk"
        )

        return TriggerCalculationResponse(
            task_id=task.id,
            message="Расчет цен запущен в фоновом режиме",
            packages_count=request.limit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": True,
                "message": f"Ошибка запуска расчета: {str(e)}",
                "error_code": "CALCULATION_ERROR",
            },
        )


@router.get(
    "/delivery/exchange-rate",
    response_model=ExchangeRateResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    },
    summary="Получить текущий курс доллара",
    description="Возвращает актуальный курс USD/RUB из кэша или ЦБ РФ"
)
async def get_exchange_rate(
    currency_provider: CurrencyRatesProvider = Depends(get_currency_provider)
):
    """
    Получить текущий курс USD/RUB.
    """
    # Пытаемся запустить фоновое обновление курсов (не критично при ошибке)
    task = None
    try:
        task = update_currency_rates.delay()
    except Exception:
        task = None

    try:
        # Получаем курс
        async with currency_provider:
            rate = await currency_provider.get_usd_to_rub_rate()

        if not rate:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": True,
                    "message": "Курс валют временно недоступен.",
                    "error_code": "RATE_NOT_AVAILABLE"
                }
            )

        # Определяем источник (по типу провайдера)
        is_cached = isinstance(currency_provider, CachedCurrencyRatesProvider)
        source = "cache" if is_cached else "CBR"

        return ExchangeRateResponse(
            task_id=(task.id if task else None),
            rate=rate.value,
            source=source,
            cached=is_cached,
            updated_at=(rate.updated_at.isoformat() if getattr(rate, "updated_at", None) else None)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": True,
                "message": f"Ошибка получения курса: {str(e)}",
                "error_code": "RATE_ERROR"
            }
        )
