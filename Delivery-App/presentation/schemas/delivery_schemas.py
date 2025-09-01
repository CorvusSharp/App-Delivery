"""
Схемы для работы с доставкой и периодическими задачами.
"""
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class TriggerCalculationRequest(BaseModel):
    """Схема запроса на принудительный расчет цен."""
    
    limit: Optional[int] = Field(
        100, 
        ge=1, 
        le=1000,
        description="Максимальное количество посылок для обработки"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "limit": 100
            }
        }


class TriggerCalculationResponse(BaseModel):
    """Схема ответа после запуска расчета цен."""
    
    task_id: str = Field(..., description="ID задачи")
    message: str = Field(..., description="Сообщение о запуске")
    packages_count: int = Field(..., description="Количество посылок к обработке")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "message": "Расчет цен запущен",
                "packages_count": 25
            }
        }


class ExchangeRateResponse(BaseModel):
    """Схема ответа с текущим курсом доллара."""
    
    task_id: Optional[str] = Field(None, description="ID Celery-задачи обновления курсов (если запущена)")
    rate: Decimal = Field(..., description="Курс USD/RUB")
    source: str = Field(..., description="Источник курса")
    cached: bool = Field(..., description="Получен из кэша")
    updated_at: Optional[str] = Field(None, description="Время последнего обновления")
    
    class Config:
        json_encoders = {
            Decimal: str
        }
        json_schema_extra = {
            "example": {
                "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "rate": "95.67",
                "source": "CBR",
                "cached": True,
                "updated_at": "2025-08-28T12:00:00Z"
            }
        }
