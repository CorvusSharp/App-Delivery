"""
Use Case: Получение деталей посылки.
"""
from application.contracts.package_dto import PackageDTO
from domain.ports.package_repository import PackageRepository
from domain.ports.package_type_repository import PackageTypeRepository
from domain.value_objects.identifiers import PackageId, SessionId
from core.exceptions import NotFoundError, ValidationError


class GetPackageDetailsUseCase:
    """Use Case для получения деталей посылки."""
    
    def __init__(
        self,
        package_repository: PackageRepository,
        package_type_repository: PackageTypeRepository
    ):
        self.package_repository = package_repository
        self.package_type_repository = package_type_repository
    
    async def execute(self, package_id: int, session_id: str) -> PackageDTO:
        """
        Получить детали посылки по ID.
        
        Args:
            package_id: ID посылки
            session_id: ID сессии пользователя
            
        Returns:
            DTO с деталями посылки
            
        Raises:
            NotFoundError: Если посылка не найдена
            ValidationError: Если данные невалидны
        """
        # Валидация входных данных
        await self._validate_input(package_id, session_id)
        
        # Получаем посылку
        domain_package_id = PackageId.from_int(package_id)
        package = await self.package_repository.get_by_id(domain_package_id)
        
        if not package:
            raise NotFoundError("Посылка", str(package_id))
        
        # Проверяем принадлежность посылки пользователю
        if package.session_id != session_id:
            raise NotFoundError("Посылка", str(package_id))
        
        # Получаем тип посылки для отображения
        package_type = await self.package_type_repository.get_by_id(package.type_id)
        
        # Конвертируем в DTO
        package_dto = PackageDTO(
            id=package.id.value,
            name=package.name,
            weight=package.weight,
            type_id=package.type_id,
            value_usd=package.value_usd,
            session_id=package.session_id,
            delivery_price_rub=package.delivery_price_rub,
            created_at=package.created_at,
            updated_at=package.updated_at
        )
        
        # Добавляем информацию о типе
        if package_type:
            package_dto.type_name = package_type.display_name
        
        return package_dto
    
    async def _validate_input(self, package_id: int, session_id: str) -> None:
        """Валидировать входные данные."""
        if package_id <= 0:
            raise ValidationError("ID посылки должен быть больше нуля", "package_id")
        
        # Валидация session_id
        try:
            SessionId.from_string(session_id)
        except ValueError as e:
            raise ValidationError(f"Неверный session_id: {str(e)}", "session_id")
