"""
Pydantic схемы для работы с типами посылок в API.
"""
from typing import List
from pydantic import BaseModel, Field


class PackageTypeResponse(BaseModel):
    """Схема ответа с информацией о типе посылки."""
    
    id: int = Field(..., description="ID типа посылки")
    name: str = Field(..., description="Системное название типа")
    display_name: str = Field(..., description="Человекочитаемое название")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "clothes",
                "display_name": "Одежда"
            }
        }


class PackageTypesListResponse(BaseModel):
    """Схема ответа со списком всех типов посылок."""
    
    types: List[PackageTypeResponse] = Field(..., description="Список типов посылок")
    total: int = Field(..., description="Общее количество типов")
    
    class Config:
        json_schema_extra = {
            "example": {
                "types": [
                    {"id": 1, "name": "clothes", "display_name": "Одежда"},
                    {"id": 2, "name": "electronics", "display_name": "Электроника"},
                    {"id": 3, "name": "other", "display_name": "Другое"}
                ],
                "total": 3
            }
        }
