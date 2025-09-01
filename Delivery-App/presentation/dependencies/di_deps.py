"""
Зависимости FastAPI для интеграции с DI контейнером.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from presentation.dependencies.container import di_container
from application.use_cases.register_package import RegisterPackageUseCase
from application.use_cases.get_packages import GetPackagesUseCase
from application.use_cases.get_package_details import GetPackageDetailsUseCase
from application.use_cases.get_package_types import GetPackageTypesUseCase


# Зависимости для базы данных
async def get_db_session():
    """Получить сессию базы данных."""
    async for session in di_container.get_db_session():
        yield session


# Зависимости для Use Cases
async def get_register_package_use_case(
    session: AsyncSession = Depends(get_db_session)
) -> RegisterPackageUseCase:
    """Получить use case регистрации посылки."""
    return await di_container.get_register_package_use_case(session)


async def get_get_packages_use_case(
    session: AsyncSession = Depends(get_db_session)
) -> GetPackagesUseCase:
    """Получить use case получения списка посылок."""
    return await di_container.get_get_packages_use_case(session)


async def get_get_package_details_use_case(
    session: AsyncSession = Depends(get_db_session)
) -> GetPackageDetailsUseCase:
    """Получить use case получения деталей посылки."""
    return await di_container.get_get_package_details_use_case(session)


async def get_get_package_types_use_case(
    session: AsyncSession = Depends(get_db_session)
) -> GetPackageTypesUseCase:
    """Получить use case получения типов посылок."""
    return await di_container.get_get_package_types_use_case(session)
