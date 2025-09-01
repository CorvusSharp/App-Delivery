"""
Провайдер курсов валют от ЦБ РФ.
Интеграция с https://www.cbr-xml-daily.ru/daily_json.js
"""
import asyncio
from decimal import Decimal
from typing import Optional
from datetime import datetime, timezone
import httpx
from loguru import logger

from domain.ports.currency_rates_provider import CurrencyRatesProvider
from domain.value_objects.currency import Rate, Currency
from core.config import get_settings


class CBRCurrencyRatesProvider(CurrencyRatesProvider):
    """Провайдер курсов валют от ЦБ РФ."""
    
    def __init__(self):
        self.settings = get_settings()
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager вход."""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.settings.CBR_TIMEOUT)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager выход."""
        if self._client:
            await self._client.aclose()
    
    async def get_usd_to_rub_rate(self) -> Optional[Rate]:
        """Получить текущий курс USD -> RUB."""
        return await self.get_rate(Currency.usd(), Currency.rub())
    
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
            Курс валют или None если не удалось получить
        """
        if from_currency.code == Currency.USD and to_currency.code == Currency.RUB:
            return await self._fetch_usd_to_rub_rate()
        
        logger.warning(f"Неподдерживаемая пара валют: {from_currency.code} -> {to_currency.code}")
        return None
    
    async def is_rate_available(
        self,
        from_currency: Currency,
        to_currency: Currency
    ) -> bool:
        """Проверить, доступен ли курс между валютами."""
        return (
            from_currency.code == Currency.USD and 
            to_currency.code == Currency.RUB
        )
    
    async def _fetch_usd_to_rub_rate(self) -> Optional[Rate]:
        """Получить курс USD -> RUB от ЦБ РФ."""
        for attempt in range(self.settings.CBR_RETRY_COUNT):
            try:
                logger.info(f"Запрос курса USD/RUB от ЦБ РФ (попытка {attempt + 1})")
                
                if not self._client:
                    self._client = httpx.AsyncClient(
                        timeout=httpx.Timeout(self.settings.CBR_TIMEOUT)
                    )
                
                response = await self._client.get(self.settings.CBR_API_URL)
                response.raise_for_status()
                
                data = response.json()
                
                # Парсим JSON ответ
                usd_rate, updated_at = self._parse_usd_rate(data)
                
                if usd_rate:
                    logger.info(f"Получен курс USD/RUB: {usd_rate}")
                    return Rate.usd_to_rub(usd_rate, updated_at=updated_at)
                else:
                    logger.warning("USD не найден в ответе ЦБ РФ")
                    
            except httpx.TimeoutException:
                logger.warning(f"Таймаут при запросе к ЦБ РФ (попытка {attempt + 1})")
                if attempt < self.settings.CBR_RETRY_COUNT - 1:
                    await asyncio.sleep(2 ** attempt)  # Экспоненциальная задержка
                    
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP ошибка при запросе к ЦБ РФ: {e.response.status_code}")
                if attempt < self.settings.CBR_RETRY_COUNT - 1:
                    await asyncio.sleep(2 ** attempt)
                    
            except Exception as e:
                logger.error(f"Ошибка при запросе курса от ЦБ РФ: {e}")
                if attempt < self.settings.CBR_RETRY_COUNT - 1:
                    await asyncio.sleep(2 ** attempt)
        
        logger.error("Не удалось получить курс USD/RUB от ЦБ РФ после всех попыток")
        return None
    
    def _parse_usd_rate(self, data: dict) -> tuple[Optional[Decimal], Optional[datetime]]:
        """
        Извлечь курс USD из JSON ответа ЦБ РФ.
        
        Args:
            data: JSON ответ от ЦБ РФ
            
        Returns:
            Пара (курс USD или None, время обновления или None)
        """
        try:
            # Структура ответа: {"Valute": {"USD": {"Value": 95.67, "Nominal": 1}}}
            valute = data.get("Valute", {})
            usd_data = valute.get("USD")
            
            if not usd_data:
                return None, None
            
            value = usd_data.get("Value")
            nominal = usd_data.get("Nominal", 1)
            
            if value is None:
                return None, None
            
            # Курс = Значение / Номинал
            rate = Decimal(str(value)) / Decimal(str(nominal))
            # Время обновления: предпочитаем поле Date из корня, иначе Timestamp, иначе None
            updated_at: Optional[datetime] = None
            try:
                # Пример Date: "2024-06-06T11:30:00+03:00" или "2024-06-06T11:30:00"
                date_str = data.get("Date")
                if isinstance(date_str, str):
                    updated_at = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                elif isinstance(data.get("Timestamp"), str):
                    updated_at = datetime.fromisoformat(data["Timestamp"].replace("Z", "+00:00"))
            except Exception:
                updated_at = None
            # Нормализуем в UTC
            if isinstance(updated_at, datetime) and updated_at.tzinfo is not None:
                updated_at = updated_at.astimezone(timezone.utc)
            return rate, updated_at
            
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Ошибка парсинга курса USD: {e}")
            return None, None


class MockCBRProvider(CurrencyRatesProvider):
    """Мок-провайдер для тестирования."""
    
    def __init__(self, mock_rate: Decimal = Decimal("95.50")):
        self.mock_rate = mock_rate
    
    async def get_usd_to_rub_rate(self) -> Optional[Rate]:
        """Вернуть моковый курс."""
        return Rate.usd_to_rub(self.mock_rate)
    
    async def get_rate(
        self,
        from_currency: Currency,
        to_currency: Currency
    ) -> Optional[Rate]:
        """Вернуть моковый курс для USD -> RUB."""
        if from_currency.code == Currency.USD and to_currency.code == Currency.RUB:
            return await self.get_usd_to_rub_rate()
        return None
    
    async def is_rate_available(
        self,
        from_currency: Currency,
        to_currency: Currency
    ) -> bool:
        """Проверить доступность курса."""
        return (
            from_currency.code == Currency.USD and 
            to_currency.code == Currency.RUB
        )
