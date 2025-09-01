"""
Роутер для работы с типами посылок.
GET /package-types - получить все типы посылок
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from presentation.schemas.package_type_schemas import PackageTypesListResponse, PackageTypeResponse
from presentation.schemas.error_schemas import ErrorResponse
from application.use_cases.get_package_types import GetPackageTypesUseCase
from core.exceptions import AppError

router = APIRouter()

from presentation.dependencies.di_deps import get_get_package_types_use_case


@router.get(
    "/package-types",
    response_model=PackageTypesListResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    },
    summary="Получить типы посылок",
    description="Возвращает список всех доступных типов посылок"
)
async def get_package_types(
    use_case: GetPackageTypesUseCase = Depends(get_get_package_types_use_case)
):
    """Получить все типы посылок."""
    try:
        # Выполняем use case
        package_types = await use_case.execute()
        
        # Конвертируем в схемы ответа
        types = []
        for package_type in package_types:
            types.append(PackageTypeResponse(
                id=package_type.id,
                name=package_type.name,
                display_name=package_type.display_name
            ))
        
        return PackageTypesListResponse(
            types=types,
            total=len(types)
        )
        
    except AppError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": True,
                "message": e.message,
                "error_code": e.error_code,
                "details": e.details
            }
        )
