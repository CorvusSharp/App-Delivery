"""
Абстрактный интерфейс для работы с сессиями.
Связка session_id ↔ данные (если понадобится дополнительное хранение).
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from domain.value_objects.identifiers import SessionId


class SessionRepository(ABC):
    """Абстрактный репозиторий для работы с сессиями."""
    
    @abstractmethod
    async def get_session_data(
        self, 
        session_id: SessionId
    ) -> Optional[Dict[str, Any]]:
        """
        Получить данные сессии.
        
        Args:
            session_id: ID сессии
            
        Returns:
            Данные сессии или None, если сессия не найдена
        """
        pass
    
    @abstractmethod
    async def save_session_data(
        self,
        session_id: SessionId,
        data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> None:
        """
        Сохранить данные сессии.
        
        Args:
            session_id: ID сессии
            data: Данные для сохранения
            ttl: Время жизни в секундах (опционально)
        """
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: SessionId) -> None:
        """
        Удалить сессию.
        
        Args:
            session_id: ID сессии
        """
        pass
    
    @abstractmethod
    async def session_exists(self, session_id: SessionId) -> bool:
        """
        Проверить, существует ли сессия.
        
        Args:
            session_id: ID сессии
            
        Returns:
            True, если сессия существует, False иначе
        """
        pass
    
    @abstractmethod
    async def extend_session_ttl(
        self,
        session_id: SessionId,
        ttl: int
    ) -> None:
        """
        Продлить время жизни сессии.
        
        Args:
            session_id: ID сессии
            ttl: Новое время жизни в секундах
        """
        pass
