"""
Абстрактный интерфейс для работы с типами посылок.
CRUD операции для типов посылок.
"""
from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.package_type import PackageType


class PackageTypeRepository(ABC):
    """Абстрактный репозиторий для работы с типами посылок."""
    
    @abstractmethod
    async def get_all(self) -> list[PackageType]:
        """
        Получить все типы посылок.
        
        Returns:
            Список всех типов посылок
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, type_id: int) -> Optional[PackageType]:
        """
        Получить тип посылки по ID.
        
        Args:
            type_id: ID типа посылки
            
        Returns:
            Тип посылки или None, если не найден
        """
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[PackageType]:
        """
        Получить тип посылки по названию.
        
        Args:
            name: Название типа посылки
            
        Returns:
            Тип посылки или None, если не найден
        """
        pass
    
    @abstractmethod
    async def exists(self, type_id: int) -> bool:
        """
        Проверить, существует ли тип посылки.
        
        Args:
            type_id: ID типа посылки
            
        Returns:
            True, если тип существует, False иначе
        """
        pass
