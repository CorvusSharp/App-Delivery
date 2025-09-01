# presentation/dependencies/container.py

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from infrastructure.sqlalchemy.database import AsyncSessionLocal
from infrastructure.sqlalchemy.package_repository import SQLAlchemyPackageRepository
from infrastructure.sqlalchemy.package_type_repository import SQLAlchemyPackageTypeRepository
from infrastructure.external.cbr_provider import CBRCurrencyRatesProvider
from infrastructure.external.cached_provider import CachedCurrencyRatesProvider

# Всегда используем Redis-хранилище сессий
from infrastructure.security.redis_session_repository import RedisSessionRepository

from domain.ports.package_repository import PackageRepository
from domain.ports.package_type_repository import PackageTypeRepository
from domain.ports.session_repository import SessionRepository
from domain.ports.currency_rates_provider import CurrencyRatesProvider

from application.use_cases.register_package import RegisterPackageUseCase
from application.use_cases.get_packages import GetPackagesUseCase
from application.use_cases.get_package_details import GetPackageDetailsUseCase
from application.use_cases.get_package_types import GetPackageTypesUseCase


class DIContainer:
    """Контейнер зависимостей приложения."""

    def __init__(self) -> None:
        self.settings = get_settings()
        # Полная реализация интерфейса SessionRepository (в т.ч. delete_session)
        # Всегда используем Redis-хранилище сессий; без REDIS_URL работа сессий невозможна
        self._session_repository: SessionRepository = RedisSessionRepository()
        self._currency_provider: CurrencyRatesProvider | None = None

    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    # --- Repositories ---

    def get_package_repository(self, session: AsyncSession) -> PackageRepository:
        return SQLAlchemyPackageRepository(session)

    def get_package_type_repository(
        self, session: AsyncSession
    ) -> PackageTypeRepository:
        return SQLAlchemyPackageTypeRepository(session)

    def get_session_repository(self) -> SessionRepository:
        return self._session_repository

    # --- External providers ---

    def get_currency_rates_provider(self) -> CurrencyRatesProvider:
        # Если доступен Redis — используем кэшируемый провайдер
        if self.settings.REDIS_URL:
            return CachedCurrencyRatesProvider(ttl_seconds=600)
        return CBRCurrencyRatesProvider()

    # --- Use cases ---

    async def get_register_package_use_case(
        self, session: AsyncSession
    ) -> RegisterPackageUseCase:
        return RegisterPackageUseCase(
            self.get_package_repository(session),
            self.get_package_type_repository(session),
        )

    async def get_get_packages_use_case(
        self, session: AsyncSession
    ) -> GetPackagesUseCase:
        return GetPackagesUseCase(
            self.get_package_repository(session),
            self.get_package_type_repository(session),
        )

    async def get_get_package_details_use_case(
        self, session: AsyncSession
    ) -> GetPackageDetailsUseCase:
        return GetPackageDetailsUseCase(
            self.get_package_repository(session),
            self.get_package_type_repository(session),
        )

    async def get_get_package_types_use_case(
        self, session: AsyncSession
    ) -> GetPackageTypesUseCase:
        return GetPackageTypesUseCase(self.get_package_type_repository(session))


# Глобальный контейнер для зависимостей FastAPI
di_container = DIContainer()
