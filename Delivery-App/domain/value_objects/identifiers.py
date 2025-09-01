"""
Value Objects для идентификаторов.
VO: PackageId, SessionId (примитивы-обёртки).
"""
from dataclasses import dataclass
from typing import Union
import uuid


@dataclass(frozen=True)
class PackageId:
    """Value Object для ID посылки."""
    
    value: int
    
    def __post_init__(self):
        """Валидация ID."""
        if not isinstance(self.value, int):
            raise TypeError("Package ID должен быть целым числом")
        
        # Разрешаем 0 как временное значение для новых сущностей (до сохранения в БД)
        if self.value < 0:
            raise ValueError("Package ID не может быть отрицательным")
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __int__(self) -> int:
        return self.value
    
    @classmethod
    def from_int(cls, value: int) -> "PackageId":
        """Создать PackageId из целого числа."""
        return cls(value=value)


@dataclass(frozen=True)
class SessionId:
    """Value Object для ID сессии."""
    
    value: str
    
    def __post_init__(self):
        """Валидация ID сессии."""
        if not isinstance(self.value, str):
            raise TypeError("Session ID должен быть строкой")
        
        if not self.value.strip():
            raise ValueError("Session ID не может быть пустым")
        
        # Проверяем, что это валидный UUID
        try:
            uuid.UUID(self.value)
        except ValueError:
            raise ValueError("Session ID должен быть валидным UUID")
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> "SessionId":
        """Создать SessionId из строки."""
        return cls(value=value)
    
    @classmethod
    def generate(cls) -> "SessionId":
        """Сгенерировать новый SessionId."""
        return cls(value=str(uuid.uuid4()))
