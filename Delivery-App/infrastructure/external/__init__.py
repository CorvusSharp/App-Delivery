"""Инициализация модуля infrastructure/external."""

from .cbr_provider import CBRCurrencyRatesProvider, MockCBRProvider

__all__ = [
    "CBRCurrencyRatesProvider",
    "MockCBRProvider"
]
