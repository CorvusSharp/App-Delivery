"""
Схемы для проверки здоровья сервиса.
"""
from typing import Dict, Any
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Схема ответа проверки здоровья."""
    
    status: str = Field(..., description="Статус сервиса")
    version: str = Field(..., description="Версия приложения")
    timestamp: str = Field(..., description="Время проверки")
    checks: Dict[str, Any] = Field(..., description="Результаты проверок")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2025-08-28T12:00:00Z",
                "checks": {
                    "database": {"status": "healthy", "response_time": "0.05s"},
                    "cbr_api": {"status": "healthy", "response_time": "0.20s"}
                }
            }
        }
