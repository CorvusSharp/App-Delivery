"""
Use Case: Регистрация посылки.
UC: валидация входа, вызов repo.save, возврат ID для сессии.
"""
from application.contracts.package_dto import CreatePackageDTO, PackageDTO
from domain.entities.package import Package
from domain.ports.package_repository import PackageRepository
from domain.ports.package_type_repository import PackageTypeRepository
from domain.value_objects.identifiers import PackageId, SessionId
from core.exceptions import ValidationError, NotFoundError


class RegisterPackageUseCase:
    """Use Case для регистрации новой посылки."""
    
    def __init__(
        self,
        package_repository: PackageRepository,
        package_type_repository: PackageTypeRepository
    ):
        self.package_repository = package_repository
        self.package_type_repository = package_type_repository
    
    async def execute(self, dto: CreatePackageDTO) -> PackageDTO:
        """
        Зарегистрировать новую посылку.
        
        Args:
            dto: Данные для создания посылки
            
        Returns:
            DTO созданной посылки
            
        Raises:
            ValidationError: Если данные невалидны
            NotFoundError: Если тип посылки не найден
        """
        # Валидация входных данных
        await self._validate_input(dto)
        
        # Проверяем, что тип посылки существует
        if not await self.package_type_repository.exists(dto.type_id):
            raise NotFoundError("Тип посылки", str(dto.type_id))
        
        # Создаем доменную сущность
        package = Package(
            id=PackageId.from_int(0),  # ID будет присвоен при сохранении
            name=dto.name.strip(),
            weight=dto.weight,
            type_id=dto.type_id,
            value_usd=dto.value_usd,
            session_id=dto.session_id
        )
        
        # Сохраняем в репозитории
        saved_package = await self.package_repository.save(package)
        
        # Возвращаем DTO
        return self._to_dto(saved_package)
    
    async def _validate_input(self, dto: CreatePackageDTO) -> None:
        """Валидировать входные данные."""
        if not dto.name or not dto.name.strip():
            raise ValidationError("Название посылки не может быть пустым", "name")
        
        if dto.weight <= 0:
            raise ValidationError("Вес посылки должен быть больше нуля", "weight")
        
        if dto.value_usd < 0:
            raise ValidationError("Стоимость посылки не может быть отрицательной", "value_usd")
        
        if dto.type_id <= 0:
            raise ValidationError("Неверный тип посылки", "type_id")
        
        # Валидация session_id
        try:
            SessionId.from_string(dto.session_id)
        except ValueError as e:
            raise ValidationError(f"Неверный session_id: {str(e)}", "session_id")
    
    def _to_dto(self, package: Package) -> PackageDTO:
        """Конвертировать доменную сущность в DTO."""
        return PackageDTO(
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
