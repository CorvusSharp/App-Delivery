"""
Задачи для расчета стоимости доставки.
"""
from loguru import logger
from infrastructure.tasks.celery_app import celery_app
from infrastructure.sqlalchemy.database import create_session_factory_no_pool
from domain.services.delivery_pricing import DeliveryPricingService
from domain.ports.currency_rates_provider import CurrencyRatesProvider
from infrastructure.sqlalchemy.package_repository import SQLAlchemyPackageRepository
from presentation.dependencies.container import di_container
from domain.ports.session_repository import SessionRepository
from domain.value_objects.identifiers import PackageId


@celery_app.task(bind=True, max_retries=2)
def calculate_delivery_prices(self, limit: int = 100):
    """
    Рассчитать стоимость доставки для посылок без цены (bulk).
    Обычно запускается вручную через админский POST /delivery/calculate,
    а по расписанию выполняется как редкий catch-up раз в час.
    """
    try:
        logger.info(f"Запуск расчета стоимости доставки (лимит: {limit})")
        
        async def process_packages():
            session_factory = create_session_factory_no_pool()
            async with session_factory() as session:
                # Репозитории
                package_repo = SQLAlchemyPackageRepository(session)
                
                # Получаем посылки без цены
                packages = await package_repo.get_packages_without_price(limit)
                
                if not packages:
                    logger.info("Нет посылок для расчета стоимости доставки")
                    return {"status": "success", "processed": 0, "message": "Нет посылок для обработки"}
                
                logger.info(f"Найдено {len(packages)} посылок для расчета")
                
                # Получаем курс валют через провайдер из DI
                provider: CurrencyRatesProvider = di_container.get_currency_rates_provider()
                async with provider:  # type: ignore[attr-defined]
                    rate = await provider.get_usd_to_rub_rate()
                
                if not rate:
                    logger.warning("Не удалось получить курс USD/RUB")
                    return {"status": "error", "message": "Курс валют недоступен"}
                
                # Сервис расчета
                pricing_service = DeliveryPricingService()
                
                # Рассчитываем цены
                processed_count = 0
                errors = []
                prices_batch: dict[int, float] = {}

                for package in packages:
                    try:
                        delivery_price = pricing_service.calculate_delivery_price(package, rate)
                        # Сохраняем для батч‑обновления (как float для совместимости с Numeric)
                        prices_batch[package.id.value] = float(delivery_price)
                    except Exception as e:
                        error_msg = f"Ошибка расчета для посылки {package.id.value}: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)

                if prices_batch:
                    processed_count = await package_repo.update_delivery_prices(prices_batch)
                    await session.commit()

                result = {
                    "status": "success",
                    "processed": processed_count,
                    "errors": len(errors),
                    "rate_used": str(rate.value)
                }
                
                if errors:
                    result["error_details"] = errors[:5]  # Первые 5 ошибок
                
                logger.info(f"Завершен расчет: обработано {processed_count} посылок, ошибок {len(errors)}")
                return result
        
        import asyncio
        return asyncio.run(process_packages())
        
    except Exception as exc:
        logger.error(f"Критическая ошибка при расчете стоимости доставки: {exc}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"Повтор задачи через 10 минут (попытка {self.request.retries + 1})")
            raise self.retry(countdown=600, exc=exc)
        else:
            return {
                "status": "error",
                "message": f"Критическая ошибка: {str(exc)}"
            }


@celery_app.task(bind=True, max_retries=2)
def calculate_package_price(self, package_id: int):
    """
    Рассчитать стоимость доставки для одной посылки.

    Используется для точечного пересчёта сразу после создания/обновления
    или по явному триггеру.
    """
    async def _process_one() -> dict:
        session_factory = create_session_factory_no_pool()
        async with session_factory() as session:
            repo = SQLAlchemyPackageRepository(session)

            # Получаем посылку
            pkg = await repo.get_by_id(PackageId.from_int(package_id))
            if not pkg:
                return {"status": "error", "message": f"Package {package_id} not found"}

            # Курс валют
            provider: CurrencyRatesProvider = di_container.get_currency_rates_provider()
            async with provider:  # type: ignore[attr-defined]
                rate = await provider.get_usd_to_rub_rate()
            if not rate:
                return {"status": "error", "message": "Rate not available"}

            # Расчёт
            pricing = DeliveryPricingService()
            try:
                new_price = pricing.calculate_delivery_price(pkg, rate)
            except Exception as e:
                logger.error(f"Failed to calculate price for package {package_id}: {e}")
                return {"status": "error", "message": str(e)}

            # Сохранение
            pkg.delivery_price_rub = new_price
            await repo.save(pkg)
            await session.commit()

            return {
                "status": "success",
                "package_id": package_id,
                "price": float(new_price),
                "rate_used": str(rate.value),
            }

    try:
        import asyncio
        return asyncio.run(_process_one())
    except Exception as exc:
        if hasattr(self, "request") and self.request.retries < self.max_retries:
            raise self.retry(countdown=120, exc=exc)
        return {"status": "error", "message": str(exc)}


@celery_app.task
def cleanup_expired_sessions():
    """
    Очистить истекшие сессии.
    Выполняется ежедневно.
    """
    try:
        logger.info("Запуск очистки истекших сессий")

        async def cleanup():
            # В текущем контракте SessionRepository нет метода очистки TTL.
            # Если понадобится — добавить в порт. Пока просто возвращаем 0.
            repo: SessionRepository = di_container.get_session_repository()
            # Ничего не делаем, так как нет метода в порту
            _ = repo  # заглушка, чтобы избежать предупреждения о неиспользуемой переменной
            return 0

        import asyncio
        expired_count = asyncio.run(cleanup())
        logger.info(f"Очищено {expired_count} истекших сессий")
        return {
            "status": "success",
            "expired_sessions": expired_count,
        }

    except Exception as exc:
        logger.error(f"Ошибка при очистке сессий: {exc}")
        return {
            "status": "error",
            "message": str(exc),
        }


@celery_app.task
def get_packages_without_price_count():
    """
    Получить количество посылок без рассчитанной цены (для мониторинга).
    """
    try:
        async def count_packages():
            session_factory = create_session_factory_no_pool()
            async with session_factory() as session:
                package_repo = SQLAlchemyPackageRepository(session)
                packages = await package_repo.get_packages_without_price(limit=1000)
                return len(packages)

        import asyncio
        count = asyncio.run(count_packages())
        
        return {
            "status": "success",
            "packages_without_price": count
        }
        
    except Exception as exc:
        logger.error(f"Ошибка при подсчете посылок: {exc}")
        return {
            "status": "error",
            "message": str(exc)
        }
