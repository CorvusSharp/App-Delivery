"""
Зависимости для управления сессиями без авторизации.
Cookie-based сессии для отслеживания пользователей.
"""
import uuid
from typing import Optional
from fastapi import Request, Response, Depends, HTTPException

from core.config import get_settings


def get_or_create_session_id(
    request: Request, 
    response: Response
) -> str:
    """
    Получить или создать ID сессии из cookies.
    
    Args:
        request: FastAPI запрос
        response: FastAPI ответ
        
    Returns:
        ID сессии
    """
    settings = get_settings()
    
    # Пытаемся получить существующую сессию
    session_id = request.cookies.get(settings.SESSION_COOKIE_NAME)
    
    if session_id and _is_valid_session_id(session_id):
        return session_id
    
    # Создаем новую сессию
    new_session_id = str(uuid.uuid4())
    
    # Устанавливаем cookie
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=new_session_id,
        max_age=settings.SESSION_COOKIE_MAX_AGE,
        secure=settings.SESSION_COOKIE_SECURE,
        httponly=settings.SESSION_COOKIE_HTTPONLY,
        samesite=settings.SESSION_COOKIE_SAMESITE,
    )
    
    return new_session_id


def get_session_id(request: Request) -> str:
    """
    Получить ID сессии из cookies (только для чтения).
    
    Args:
        request: FastAPI запрос
        
    Returns:
        ID сессии
        
    Raises:
        HTTPException: Если сессия не найдена
    """
    settings = get_settings()
    
    session_id = request.cookies.get(settings.SESSION_COOKIE_NAME)
    
    if not session_id or not _is_valid_session_id(session_id):
        raise HTTPException(
            status_code=401,
            detail="Сессия не найдена. Зарегистрируйте посылку для создания сессии."
        )
    
    return session_id


def get_optional_session_id(request: Request) -> Optional[str]:
    """
    Получить ID сессии из cookies (опционально).
    
    Args:
        request: FastAPI запрос
        
    Returns:
        ID сессии или None
    """
    settings = get_settings()
    
    session_id = request.cookies.get(settings.SESSION_COOKIE_NAME)
    
    if session_id and _is_valid_session_id(session_id):
        return session_id
    
    return None


def _is_valid_session_id(session_id: str) -> bool:
    """
    Проверить валидность ID сессии.
    
    Args:
        session_id: ID сессии для проверки
        
    Returns:
        True если ID валиден, False иначе
    """
    if not session_id:
        return False
    
    # Проверяем формат UUID
    try:
        uuid.UUID(session_id)
        return True
    except ValueError:
        return False


class SessionDependency:
    """Класс для управления зависимостями сессий."""
    
    def __init__(self, auto_create: bool = True):
        """
        Инициализация.
        
        Args:
            auto_create: Автоматически создавать сессию если её нет
        """
        self.auto_create = auto_create
    
    def __call__(self, request: Request, response: Response) -> str:
        """
        Dependency для получения/создания сессии.
        
        Args:
            request: FastAPI запрос
            response: FastAPI ответ
            
        Returns:
            ID сессии
        """
        if self.auto_create:
            return get_or_create_session_id(request, response)
        else:
            return get_session_id(request)


# Предконфигурированные dependency
auto_session = SessionDependency(auto_create=True)
require_session = SessionDependency(auto_create=False)
