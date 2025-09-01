"""
Use Case: Получение всех типов посылок.
"""
from typing import List
from domain.ports.package_type_repository import PackageTypeRepository
from domain.entities.package_type import PackageType


class GetPackageTypesUseCase:
    """Use Case для получения всех типов посылок."""
    
    def __init__(self, package_type_repository: PackageTypeRepository):
        self.package_type_repository = package_type_repository
    
    async def execute(self) -> List[PackageType]:
        """
        Получить все доступные типы посылок.
        
        Returns:
            Список типов посылок
        """
        return await self.package_type_repository.get_all()
