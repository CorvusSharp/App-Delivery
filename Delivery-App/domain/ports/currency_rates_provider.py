"""
Абстрактный интерфейс для получения курсов валют.
Порт получения курса USD→RUB (снаружи: CBR + кэш).
"""
from abc import ABC, abstractmethod
from typing import Optional

from domain.value_objects.currency import Rate, Currency


class CurrencyRatesProvider(ABC):
    """Абстрактный провайдер курсов валют."""
    
    @abstractmethod
    async def get_usd_to_rub_rate(self) -> Optional[Rate]:
        """
        Получить текущий курс USD -> RUB.
        
        Returns:
            Курс USD -> RUB или None, если не удалось получить
        """
        pass
    
    @abstractmethod
    async def get_rate(
        self,
        from_currency: Currency,
        to_currency: Currency
    ) -> Optional[Rate]:
        """
        Получить курс между двумя валютами.
        
        Args:
            from_currency: Исходная валюта
            to_currency: Целевая валюта
            
        Returns:
            Курс валют или None, если не удалось получить
        """
        pass
    
    @abstractmethod
    async def is_rate_available(
        self,
        from_currency: Currency,
        to_currency: Currency
    ) -> bool:
        """
        Проверить, доступен ли курс между валютами.
        
        Args:
            from_currency: Исходная валюта
            to_currency: Целевая валюта
            
        Returns:
            True, если курс доступен, False иначе
        """
        pass
