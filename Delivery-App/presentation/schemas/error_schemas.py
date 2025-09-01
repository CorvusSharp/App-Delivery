"""
Pydantic схемы для стандартизации ошибок API.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Детали ошибки."""
    
    field: Optional[str] = Field(None, description="Поле с ошибкой")
    message: str = Field(..., description="Сообщение об ошибке")
    code: Optional[str] = Field(None, description="Код ошибки")


class ErrorResponse(BaseModel):
    """Стандартная схема ответа с ошибкой."""
    
    error: bool = Field(True, description="Флаг ошибки")
    message: str = Field(..., description="Основное сообщение об ошибке")
    error_code: str = Field(..., description="Код ошибки")
    details: Optional[Dict[str, Any]] = Field(
        None, 
        description="Дополнительные детали ошибки"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": True,
                "message": "Ошибка валидации данных",
                "error_code": "VALIDATION_ERROR",
                "details": {
                    "field": "weight",
                    "message": "Вес должен быть больше нуля"
                }
            }
        }


class ValidationErrorResponse(BaseModel):
    """Схема ответа с ошибками валидации."""
    
    error: bool = Field(True, description="Флаг ошибки")
    message: str = Field(
        default="Ошибка валидации данных", 
        description="Основное сообщение"
    )
    error_code: str = Field(
        default="VALIDATION_ERROR", 
        description="Код ошибки"
    )
    errors: list[ErrorDetail] = Field(..., description="Список ошибок валидации")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": True,
                "message": "Ошибка валидации данных",
                "error_code": "VALIDATION_ERROR",
                "errors": [
                    {
                        "field": "weight",
                        "message": "Вес должен быть больше нуля",
                        "code": "value_error.number.not_gt"
                    }
                ]
            }
        }


class SuccessResponse(BaseModel):
    """Схема успешного ответа."""
    
    success: bool = Field(True, description="Флаг успеха")
    message: str = Field(..., description="Сообщение об успехе")
    data: Optional[Dict[str, Any]] = Field(
        None, 
        description="Дополнительные данные"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Операция выполнена успешно",
                "data": {}
            }
        }
