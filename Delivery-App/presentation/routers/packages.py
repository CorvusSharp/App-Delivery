"""
Роутер для работы с посылками.
POST /packages (регистрация), GET /packages (листинг), GET /packages/{id}
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from typing import Optional

from presentation.schemas.package_schemas import (
    RegisterPackageRequest, 
    RegisterPackageResponse,
    PackageListResponse,
    PackageDetailsResponse,
    PackageListItem
)
from presentation.schemas.error_schemas import ErrorResponse
from presentation.dependencies.session_deps import auto_session, require_session
from application.use_cases.register_package import RegisterPackageUseCase
from application.use_cases.get_packages import GetPackagesUseCase
from application.use_cases.get_package_details import GetPackageDetailsUseCase
from application.contracts.package_dto import CreatePackageDTO, PackageFilterDTO
from core.exceptions import AppError, ValidationError, NotFoundError
from infrastructure.tasks.delivery_tasks import calculate_package_price


router = APIRouter()

# TODO: Dependency Injection уже настроен
from presentation.dependencies.di_deps import (
    get_register_package_use_case,
    get_get_packages_use_case,
    get_get_package_details_use_case
)


@router.post(
    "/packages", 
    response_model=RegisterPackageResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Ошибка валидации"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    },
    summary="Зарегистрировать посылку",
    description="Регистрирует новую посылку и возвращает её ID"
)
async def register_package(
    request: RegisterPackageRequest,
    response: Response,
    session_id: str = Depends(auto_session),
    use_case: RegisterPackageUseCase = Depends(get_register_package_use_case)
):
    """Зарегистрировать новую посылку."""
    try:
        # Создаем DTO
        create_dto = CreatePackageDTO(
            name=request.name,
            weight=request.weight,
            type_id=request.type_id,
            value_usd=request.value_usd,
            session_id=session_id
        )
        
        # Выполняем use case
        package_dto = await use_case.execute(create_dto)
        
        return RegisterPackageResponse(
            id=package_dto.id,
            message="Посылка успешно зарегистрирована"
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": True,
                "message": e.message,
                "error_code": e.error_code,
                "details": e.details
            }
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


@router.post(
    "/packages/{package_id}/recalculate",
    responses={
        202: {"description": "Пересчёт запущен"},
        404: {"model": ErrorResponse, "description": "Посылка не найдена"},
        400: {"model": ErrorResponse, "description": "Ошибка валидации"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"},
    },
    summary="Явный пересчёт стоимости одной посылки",
    description="Публикует задачу Celery для пересчёта цены конкретной посылки",
    status_code=202,
)
async def recalculate_package(
    package_id: int,
    session_id: str = Depends(require_session),
    use_case: GetPackageDetailsUseCase = Depends(get_get_package_details_use_case),
):
    """Триггер пересчёта одной посылки (админ/тех-сценарий)."""
    try:
        # Убедимся, что посылка принадлежит сессии и существует
        await use_case.execute(package_id, session_id)
        # Публикуем точечную задачу в отдельную очередь
        calculate_package_price.apply_async(args=[package_id], queue="pricing")
        return {"accepted": True, "package_id": package_id}
    except NotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": True,
                "message": e.message,
                "error_code": e.error_code,
                "details": e.details,
            },
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": True,
                "message": e.message,
                "error_code": e.error_code,
                "details": e.details,
            },
        )
    except AppError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": True,
                "message": e.message,
                "error_code": e.error_code,
                "details": e.details,
            },
        )


@router.get(
    "/packages", 
    response_model=PackageListResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Ошибка валидации"},
        401: {"model": ErrorResponse, "description": "Сессия не найдена"}
    },
    summary="Получить список посылок",
    description="Возвращает список посылок пользователя с фильтрацией и пагинацией"
)
async def get_packages(
    session_id: str = Depends(require_session),
    type_id: Optional[int] = Query(None, description="Фильтр по типу посылки"),
    has_price: Optional[bool] = Query(None, description="Фильтр по наличию цены"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    use_case: GetPackagesUseCase = Depends(get_get_packages_use_case)
):
    """Получить список посылок пользователя."""
    try:
        # Создаем DTO фильтров
        filters = PackageFilterDTO(
            session_id=session_id,
            type_id=type_id,
            has_price=has_price,
            offset=(page - 1) * size,
            limit=size
        )
        
        # Выполняем use case
        pagination_result = await use_case.execute(filters)
        
        # Конвертируем в схемы ответа
        items = []
        for item_dto in pagination_result.items:
            items.append(PackageListItem(
                id=item_dto.id,
                name=item_dto.name,
                weight=item_dto.weight,
                type_id=item_dto.type_id,
                type_name=item_dto.type_name,
                value_usd=item_dto.value_usd,
                delivery_price_rub=item_dto.delivery_price_rub,
                delivery_status=item_dto.status,
                created_at=item_dto.created_at
            ))
        
        return PackageListResponse(
            items=items,
            total=pagination_result.total,
            page=pagination_result.page,
            pages=pagination_result.pages,
            has_next=pagination_result.has_next,
            has_prev=pagination_result.has_prev
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": True,
                "message": e.message,
                "error_code": e.error_code,
                "details": e.details
            }
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


@router.get(
    "/packages/{package_id}", 
    response_model=PackageDetailsResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Ошибка валидации"},
        401: {"model": ErrorResponse, "description": "Сессия не найдена"},
        404: {"model": ErrorResponse, "description": "Посылка не найдена"}
    },
    summary="Получить детали посылки",
    description="Возвращает полную информацию о посылке по её ID"
)
async def get_package_details(
    package_id: int,
    session_id: str = Depends(require_session),
    use_case: GetPackageDetailsUseCase = Depends(get_get_package_details_use_case)
):
    """Получить детали посылки."""
    try:
        # Выполняем use case
        package_dto = await use_case.execute(package_id, session_id)

        # Определяем статус
        delivery_status = "calculated" if package_dto.delivery_price_rub else "pending"

    # GET не публикует задач

        return PackageDetailsResponse(
            id=package_dto.id,
            name=package_dto.name,
            weight=package_dto.weight,
            type_id=package_dto.type_id,
            type_name=package_dto.type_name or "Неизвестный",
            value_usd=package_dto.value_usd,
            delivery_price_rub=package_dto.delivery_price_rub,
            delivery_status=delivery_status,
            created_at=package_dto.created_at,
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": True,
                "message": e.message,
                "error_code": e.error_code,
                "details": e.details,
            },
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "error": True,
                "message": e.message,
                "error_code": e.error_code,
                "details": e.details,
            },
        )
    except AppError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": True,
                "message": e.message,
                "error_code": e.error_code,
                "details": e.details,
            },
        )
