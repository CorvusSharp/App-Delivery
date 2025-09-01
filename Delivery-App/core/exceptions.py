"""
Базовые исключения приложения.
Кастомные ошибки для доменной логики и API.
"""
from typing import Any, Dict, Optional


class AppError(Exception):
    """Базовое исключение приложения."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "APP_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AppError):
    """Ошибка валидации данных."""
    
    def __init__(
        self,
        message: str = "Ошибка валидации данных",
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details or {}
        )
        if field:
            self.details["field"] = field


class NotFoundError(AppError):
    """Ошибка - ресурс не найден."""
    
    def __init__(
        self,
        resource: str = "Ресурс",
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = f"{resource} не найден"
        if resource_id:
            message += f" (ID: {resource_id})"
        
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            details=details or {}
        )
        if resource_id:
            self.details["resource_id"] = resource_id


class RateLimitError(AppError):
    """Ошибка превышения лимита запросов."""
    
    def __init__(
        self,
        message: str = "Превышен лимит запросов",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT",
            details=details or {}
        )
        if retry_after:
            self.details["retry_after"] = retry_after


class ExternalServiceError(AppError):
    """Ошибка внешнего сервиса."""
    
    def __init__(
        self,
        service_name: str,
        message: str = "Ошибка внешнего сервиса",
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=f"{service_name}: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details or {}
        )
        self.details["service_name"] = service_name
        if status_code:
            self.details["status_code"] = status_code


class DatabaseError(AppError):
    """Ошибка базы данных."""
    
    def __init__(
        self,
        message: str = "Ошибка базы данных",
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details or {}
        )
        if operation:
            self.details["operation"] = operation


class CacheError(AppError):
    """Ошибка кэша."""
    
    def __init__(
        self,
        message: str = "Ошибка кэша",
        cache_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            details=details or {}
        )
        if cache_key:
            self.details["cache_key"] = cache_key


class BusinessLogicError(AppError):
    """Ошибка бизнес-логики."""
    
    def __init__(
        self,
        message: str,
        rule: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            details=details or {}
        )
        if rule:
            self.details["rule"] = rule
