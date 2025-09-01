"""
Задачи для работы с курсами валют.
"""
from loguru import logger
from typing import Optional
from infrastructure.tasks.celery_app import celery_app
from presentation.dependencies.container import di_container
from domain.ports.currency_rates_provider import CurrencyRatesProvider
from domain.value_objects.currency import Currency
import asyncio


from domain.value_objects.currency import Rate


async def _fetch_usd_rub_rate() -> Optional[Rate]:
    """Асинхронно получить курс USD->RUB через DI-провайдер.

    Возвращает value-object Currency или None.
    """
    provider: CurrencyRatesProvider = di_container.get_currency_rates_provider()
    async with provider:  # type: ignore[attr-defined]
        return await provider.get_usd_to_rub_rate()


@celery_app.task(bind=True, max_retries=3)
def update_currency_rates(self):
    """
    Обновить курсы валют от ЦБ РФ.
    Выполняется каждые 5 минут.
    """
    try:
        logger.info("Запуск задачи обновления курсов валют")
        # Получаем курс USD -> RUB через общий helper
        rate = asyncio.run(_fetch_usd_rub_rate())

        if rate:
            logger.info(f"Курс USD/RUB получен: {rate.value}")
            return {"status": "success", "rate": str(rate.value)}
        else:
            logger.warning("Не удалось получить курс валют")
            # Повторяем задачу через 2 минуты
            raise self.retry(countdown=120)

    except Exception as exc:
        logger.error(f"Ошибка при обновлении курсов валют: {exc}")

        if self.request.retries < self.max_retries:
            logger.info(
                f"Повтор задачи через 5 минут (попытка {self.request.retries + 1})"
            )
            raise self.retry(countdown=300, exc=exc)
        else:
            logger.error("Исчерпаны все попытки обновления курсов валют")
            return {
                "status": "error",
                "message": f"Не удалось обновить курсы валют: {str(exc)}",
            }

 
