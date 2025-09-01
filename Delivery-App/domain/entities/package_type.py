"""
Доменная сущность: Тип посылки.
Entity: PackageType(id, name=[clothes,electronics,other]).
"""
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class PackageType:
    """Доменная сущность типа посылки."""
    
    id: int
    name: str
    
    # Константы типов
    CLOTHES: ClassVar[str] = "clothes"
    ELECTRONICS: ClassVar[str] = "electronics"
    OTHER: ClassVar[str] = "other"
    
    # Мапинг ID -> название
    TYPE_MAPPING: ClassVar[dict[int, str]] = {
        1: CLOTHES,
        2: ELECTRONICS,
        3: OTHER,
    }
    
    # Обратный мапинг название -> ID
    NAME_TO_ID_MAPPING: ClassVar[dict[str, int]] = {
        CLOTHES: 1,
        ELECTRONICS: 2,
        OTHER: 3,
    }
    
    def __post_init__(self):
        """Валидация данных после создания."""
        if self.id not in self.TYPE_MAPPING:
            raise ValueError(f"Недопустимый ID типа посылки: {self.id}")
        
        if self.name not in self.NAME_TO_ID_MAPPING:
            raise ValueError(f"Недопустимое название типа посылки: {self.name}")
        
        if self.TYPE_MAPPING[self.id] != self.name:
            raise ValueError(f"Несоответствие ID {self.id} и названия {self.name}")
    
    @classmethod
    def get_all_types(cls) -> list["PackageType"]:
        """Получить все доступные типы посылок."""
        return [
            cls(id=type_id, name=type_name)
            for type_id, type_name in cls.TYPE_MAPPING.items()
        ]
    
    @classmethod
    def get_by_id(cls, type_id: int) -> "PackageType":
        """Получить тип посылки по ID."""
        if type_id not in cls.TYPE_MAPPING:
            raise ValueError(f"Тип посылки с ID {type_id} не найден")
        return cls(id=type_id, name=cls.TYPE_MAPPING[type_id])
    
    @classmethod
    def get_by_name(cls, name: str) -> "PackageType":
        """Получить тип посылки по названию."""
        if name not in cls.NAME_TO_ID_MAPPING:
            raise ValueError(f"Тип посылки с названием {name} не найден")
        return cls(id=cls.NAME_TO_ID_MAPPING[name], name=name)
    
    @property
    def display_name(self) -> str:
        """Получить человекочитаемое название."""
        display_names = {
            self.CLOTHES: "Одежда",
            self.ELECTRONICS: "Электроника", 
            self.OTHER: "Другое",
        }
        return display_names.get(self.name, self.name)
