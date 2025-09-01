"""
Value Objects для валют и курсов.
VO: Currency(code="USD"/"RUB"), Rate(value: Decimal).
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import ClassVar
from datetime import datetime


@dataclass(frozen=True)
class Currency:
    """Value Object для валюты."""
    
    code: str
    
    # Поддерживаемые валюты
    USD: ClassVar[str] = "USD"
    RUB: ClassVar[str] = "RUB"
    
    SUPPORTED_CURRENCIES: ClassVar[set[str]] = {USD, RUB}
    
    def __post_init__(self):
        """Валидация кода валюты."""
        if self.code not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Неподдерживаемая валюта: {self.code}")
    
    @classmethod
    def usd(cls) -> "Currency":
        """Создать USD валюту."""
        return cls(code=cls.USD)
    
    @classmethod
    def rub(cls) -> "Currency":
        """Создать RUB валюту."""
        return cls(code=cls.RUB)


@dataclass(frozen=True)
class Rate:
    """Value Object для курса валют."""
    
    value: Decimal
    from_currency: Currency
    to_currency: Currency
    # Время, на которое актуален курс (по данным провайдера)
    updated_at: datetime | None = None
    
    def __post_init__(self):
        """Валидация курса."""
        if self.value <= 0:
            raise ValueError("Курс валют должен быть больше нуля")
        
        if self.from_currency.code == self.to_currency.code:
            raise ValueError("Валюты должны быть разными")
    
    @classmethod
    def usd_to_rub(cls, rate_value: Decimal, updated_at: datetime | None = None) -> "Rate":
        """Создать курс USD -> RUB."""
        return cls(
            value=rate_value,
            from_currency=Currency.usd(),
            to_currency=Currency.rub(),
            updated_at=updated_at,
        )
    
    def convert(self, amount: Decimal) -> Decimal:
        """Конвертировать сумму по курсу."""
        if amount < 0:
            raise ValueError("Сумма не может быть отрицательной")
        return amount * self.value
    
    @property
    def rate_float(self) -> float:
        """Получить курс как float."""
        return float(self.value)
