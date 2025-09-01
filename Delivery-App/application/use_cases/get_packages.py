"""
Use Case: Получение списка посылок пользователя.
"""
from application.contracts.package_dto import PackageListItemDTO, PackageFilterDTO
from application.contracts.pagination import PaginationDTO
from domain.ports.package_repository import PackageRepository
from domain.ports.package_type_repository import PackageTypeRepository
from domain.value_objects.identifiers import SessionId
from core.exceptions import ValidationError


class GetPackagesUseCase:
    """Use Case для получения списка посылок пользователя."""
    
    def __init__(
        self,
        package_repository: PackageRepository,
        package_type_repository: PackageTypeRepository
    ):
        self.package_repository = package_repository
        self.package_type_repository = package_type_repository
    
    async def execute(self, filters: PackageFilterDTO) -> PaginationDTO[PackageListItemDTO]:
        """
        Получить список посылок с фильтрами и пагинацией.
        
        Args:
            filters: Фильтры для поиска
            
        Returns:
            Пагинированный список посылок
        """
        # Валидация входных данных
        await self._validate_filters(filters)
        
        # Получаем session_id
        session_id = SessionId.from_string(filters.session_id)
        
        # Получаем общее количество
        total_count = await self.package_repository.count_by_session_id(
            session_id=session_id,
            type_id=filters.type_id,
            has_price=filters.has_price
        )
        
        # Получаем посылки для текущей страницы
        packages = await self.package_repository.get_by_session_id(
            session_id=session_id,
            type_id=filters.type_id,
            has_price=filters.has_price,
            offset=filters.offset,
            limit=filters.limit
        )
        
        # Получаем типы посылок для маппинга
        package_types = await self.package_type_repository.get_all()
        type_mapping = {t.id: t for t in package_types}
        
        # Конвертируем в DTO
        items = []
        for package in packages:
            package_type = type_mapping.get(package.type_id)
            type_name = package_type.display_name if package_type else "Неизвестный"
            
            items.append(PackageListItemDTO(
                id=package.id.value,
                name=package.name,
                weight=package.weight,
                type_id=package.type_id,
                type_name=type_name,
                value_usd=package.value_usd,
                delivery_price_rub=package.delivery_price_rub,
                status=package.get_display_status(),
                created_at=package.created_at
            ))
        
        # Создаем пагинацию
        page_size = filters.limit
        current_page = (filters.offset // page_size) + 1
        total_pages = (total_count + page_size - 1) // page_size
        
        return PaginationDTO(
            items=items,
            total=total_count,
            page=current_page,
            pages=total_pages,
            size=page_size,
            has_next=current_page < total_pages,
            has_prev=current_page > 1
        )
    
    async def _validate_filters(self, filters: PackageFilterDTO) -> None:
        """Валидировать фильтры."""
        if filters.limit <= 0:
            raise ValidationError("Лимит должен быть больше нуля", "limit")
        
        if filters.limit > 100:
            raise ValidationError("Лимит не должен превышать 100", "limit")
        
        if filters.offset < 0:
            raise ValidationError("Смещение не может быть отрицательным", "offset")
        
        if filters.type_id is not None:
            if filters.type_id <= 0 or filters.type_id > 3:
                raise ValidationError("Неверный тип посылки", "type_id")
        
        # Валидация session_id
        try:
            SessionId.from_string(filters.session_id)
        except ValueError as e:
            raise ValidationError(f"Неверный session_id: {str(e)}", "session_id")
