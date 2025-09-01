"""
Доменная сущность: Посылка.
Entity: Package(id, name, weight, type_id, value_usd, delivery_price_rub).
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from datetime import datetime

from domain.value_objects.identifiers import PackageId


@dataclass
class Package:
    """Доменная сущность посылки."""
    
    id: PackageId
    name: str
    weight: Decimal  # в килограммах
    type_id: int
    value_usd: Decimal  # стоимость в долларах
    session_id: str
    delivery_price_rub: Optional[Decimal] = None  # цена доставки в рублях
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Валидация данных после создания."""
        if self.weight <= 0:
            raise ValueError("Вес посылки должен быть больше нуля")
        
        if self.value_usd < 0:
            raise ValueError("Стоимость посылки не может быть отрицательной")
        
        if self.name.strip() == "":
            raise ValueError("Название посылки не может быть пустым")
    
    @property
    def has_calculated_price(self) -> bool:
        """Проверить, рассчитана ли цена доставки."""
        return self.delivery_price_rub is not None
    
    @property
    def weight_kg(self) -> float:
        """Получить вес в килограммах как float."""
        return float(self.weight)
    
    @property
    def value_usd_float(self) -> float:
        """Получить стоимость в долларах как float."""
        return float(self.value_usd)
    
    def set_delivery_price(self, price_rub: Decimal) -> None:
        """Установить цену доставки."""
        if price_rub < 0:
            raise ValueError("Цена доставки не может быть отрицательной")
        self.delivery_price_rub = price_rub
    
    def get_display_status(self) -> str:
        """Получить статус для отображения."""
        if self.has_calculated_price:
            return "calculated"
        return "pending"
