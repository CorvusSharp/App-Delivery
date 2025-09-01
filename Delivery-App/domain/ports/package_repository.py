"""
Абстрактный интерфейс для работы с посылками.
Сохранить/получить/листинг с пагинацией и фильтрами.
"""
from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.package import Package
from domain.value_objects.identifiers import PackageId, SessionId


class PackageRepository(ABC):
    """Абстрактный репозиторий для работы с посылками."""
    
    @abstractmethod
    async def save(self, package: Package) -> Package:
        """
        Сохранить посылку.
        
        Args:
            package: Посылка для сохранения
            
        Returns:
            Сохранённая посылка с ID
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, package_id: PackageId) -> Optional[Package]:
        """
        Получить посылку по ID.
        
        Args:
            package_id: ID посылки
            
        Returns:
            Посылка или None, если не найдена
        """
        pass
    
    @abstractmethod
    async def get_by_session_id(
        self,
        session_id: SessionId,
        type_id: Optional[int] = None,
        has_price: Optional[bool] = None,
        offset: int = 0,
        limit: int = 100
    ) -> list[Package]:
        """
        Получить посылки по session_id с фильтрами и пагинацией.
        
        Args:
            session_id: ID сессии
            type_id: Фильтр по типу посылки (опционально)
            has_price: Фильтр по наличию рассчитанной цены (опционально)
            offset: Смещение для пагинации
            limit: Лимит записей
            
        Returns:
            Список посылок
        """
        pass
    
    @abstractmethod
    async def count_by_session_id(
        self,
        session_id: SessionId,
        type_id: Optional[int] = None,
        has_price: Optional[bool] = None
    ) -> int:
        """
        Подсчитать количество посылок по session_id с фильтрами.
        
        Args:
            session_id: ID сессии
            type_id: Фильтр по типу посылки (опционально)
            has_price: Фильтр по наличию рассчитанной цены (опционально)
            
        Returns:
            Количество посылок
        """
        pass
    
    @abstractmethod
    async def get_packages_without_price(
        self,
        limit: int = 100
    ) -> list[Package]:
        """
        Получить посылки без рассчитанной цены доставки.
        
        Args:
            limit: Максимальное количество записей
            
        Returns:
            Список посылок без цены
        """
        pass
    
    @abstractmethod
    async def update_delivery_prices(
        self,
        package_prices: dict[int, float]
    ) -> int:
        """
        Массово обновить цены доставки для посылок.
        
        Args:
            package_prices: Словарь {package_id: delivery_price_rub}
            
        Returns:
            Количество обновлённых записей
        """
        pass
