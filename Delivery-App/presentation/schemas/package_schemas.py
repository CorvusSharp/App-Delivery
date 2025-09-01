"""
Pydantic схемы для работы с посылками в API.
Валидация входящих запросов и форматирование ответов.
"""
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class RegisterPackageRequest(BaseModel):
    """Схема запроса на регистрацию посылки."""
    
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=200,
        description="Название посылки"
    )
    weight: Decimal = Field(
        ..., 
        gt=0, 
        decimal_places=3,
        description="Вес посылки в килограммах"
    )
    type_id: int = Field(
        ..., 
        ge=1, 
        le=3,
        description="ID типа посылки (1-одежда, 2-электроника, 3-разное)"
    )
    value_usd: Decimal = Field(
        ..., 
        ge=0, 
        decimal_places=2,
        description="Стоимость содержимого в долларах"
    )
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Название посылки не может быть пустым')
        return v.strip()
    
    class Config:
        json_encoders = {
            Decimal: str
        }
        json_schema_extra = {
            "example": {
                "name": "Зимняя куртка",
                "weight": "1.250",
                "type_id": 1,
                "value_usd": "150.00"
            }
        }


class RegisterPackageResponse(BaseModel):
    """Схема ответа после регистрации посылки."""
    
    id: int = Field(..., description="Уникальный ID посылки")
    message: str = Field(default="Посылка успешно зарегистрирована")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "message": "Посылка успешно зарегистрирована"
            }
        }


class PackageDetailsResponse(BaseModel):
    """Схема ответа с деталями посылки."""
    
    id: int = Field(..., description="ID посылки")
    name: str = Field(..., description="Название посылки")
    weight: Decimal = Field(..., description="Вес в килограммах")
    type_id: int = Field(..., description="ID типа посылки")
    type_name: str = Field(..., description="Название типа посылки")
    value_usd: Decimal = Field(..., description="Стоимость в долларах")
    delivery_price_rub: Optional[Decimal] = Field(
        None, 
        description="Стоимость доставки в рублях"
    )
    delivery_status: str = Field(..., description="Статус расчета доставки")
    created_at: datetime = Field(..., description="Дата создания")
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "id": 123,
                "name": "Зимняя куртка",
                "weight": "1.250",
                "type_id": 1,
                "type_name": "Одежда",
                "value_usd": "150.00",
                "delivery_price_rub": "1875.50",
                "delivery_status": "calculated",
                "created_at": "2025-08-28T12:00:00"
            }
        }


class PackageListItem(BaseModel):
    """Схема элемента списка посылок."""
    
    id: int = Field(..., description="ID посылки")
    name: str = Field(..., description="Название посылки") 
    weight: Decimal = Field(..., description="Вес в килограммах")
    type_id: int = Field(..., description="ID типа посылки")
    type_name: str = Field(..., description="Название типа посылки")
    value_usd: Decimal = Field(..., description="Стоимость в долларах")
    delivery_price_rub: Optional[Decimal] = Field(
        None, 
        description="Стоимость доставки в рублях"
    )
    delivery_status: str = Field(..., description="Статус расчета доставки")
    created_at: datetime = Field(..., description="Дата создания")
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


class PackageListResponse(BaseModel):
    """Схема ответа со списком посылок."""
    
    items: List[PackageListItem] = Field(..., description="Список посылок")
    total: int = Field(..., description="Общее количество посылок")
    page: int = Field(..., description="Текущая страница")
    pages: int = Field(..., description="Общее количество страниц")
    has_next: bool = Field(..., description="Есть ли следующая страница")
    has_prev: bool = Field(..., description="Есть ли предыдущая страница")
    
    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {
                        "id": 123,
                        "name": "Зимняя куртка",
                        "weight": "1.250",
                        "type_id": 1,
                        "type_name": "Одежда",
                        "value_usd": "150.00",
                        "delivery_price_rub": "1875.50",
                        "delivery_status": "calculated",
                        "created_at": "2025-08-28T12:00:00"
                    }
                ],
                "total": 1,
                "page": 1,
                "pages": 1,
                "has_next": False,
                "has_prev": False
            }
        }


class PackageFilters(BaseModel):
    """Схема фильтров для поиска посылок."""
    
    type_id: Optional[int] = Field(
        None, 
        ge=1, 
        le=3,
        description="Фильтр по типу посылки"
    )
    has_price: Optional[bool] = Field(
        None,
        description="Фильтр по наличию рассчитанной цены доставки"
    )
    page: int = Field(
        1, 
        ge=1,
        description="Номер страницы"
    )
    size: int = Field(
        20, 
        ge=1, 
        le=100,
        description="Размер страницы"
    )
