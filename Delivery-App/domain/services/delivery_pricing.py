"""
Доменный сервис для расчёта стоимости доставки.
Правила расчёта: (kg*0.5 + usd*0.01) * usd_to_rub.
"""
from decimal import Decimal

from domain.entities.package import Package
from domain.value_objects.currency import Rate


class DeliveryPricingService:
    """Доменный сервис для расчёта стоимости доставки."""
    
    # Коэффициенты для расчёта
    WEIGHT_COEFFICIENT = Decimal("0.5")  # 0.5 USD за кг
    VALUE_COEFFICIENT = Decimal("0.01")  # 1% от стоимости
    
    def calculate_delivery_price(
        self, 
        package: Package, 
        usd_to_rub_rate: Rate
    ) -> Decimal:
        """
        Рассчитать стоимость доставки посылки.
        
        Формула: (вес_кг * 0.5 + стоимость_usd * 0.01) * курс_USD_RUB
        
        Args:
            package: Посылка для расчёта
            usd_to_rub_rate: Курс USD -> RUB
            
        Returns:
            Стоимость доставки в рублях
        """
        # Базовая стоимость в USD
        weight_cost_usd = package.weight * self.WEIGHT_COEFFICIENT
        value_cost_usd = package.value_usd * self.VALUE_COEFFICIENT
        
        total_cost_usd = weight_cost_usd + value_cost_usd
        
        # Конвертация в рубли
        total_cost_rub = usd_to_rub_rate.convert(total_cost_usd)
        
        # Округляем до 2 знаков после запятой
        return total_cost_rub.quantize(Decimal("0.01"))
    
    def calculate_delivery_prices_bulk(
        self,
        packages: list[Package],
        usd_to_rub_rate: Rate
    ) -> dict[int, Decimal]:
        """
        Рассчитать стоимость доставки для множества посылок.
        
        Args:
            packages: Список посылок
            usd_to_rub_rate: Курс USD -> RUB
            
        Returns:
            Словарь {package_id: delivery_price_rub}
        """
        results = {}
        
        for package in packages:
            try:
                price = self.calculate_delivery_price(package, usd_to_rub_rate)
                results[package.id.value] = price
            except Exception:
                # В случае ошибки пропускаем пакет
                # Логирование должно быть на уровне приложения
                continue
        
        return results
    
    def validate_calculation_inputs(
        self, 
        package: Package, 
        rate: Rate
    ) -> None:
        """
        Валидировать входные данные для расчёта.
        
        Args:
            package: Посылка
            rate: Курс валют
            
        Raises:
            ValueError: Если данные невалидны
        """
        if package.weight <= 0:
            raise ValueError("Вес посылки должен быть больше нуля")
        
        if package.value_usd < 0:
            raise ValueError("Стоимость посылки не может быть отрицательной")
        
        if rate.value <= 0:
            raise ValueError("Курс валют должен быть больше нуля")
        
        # Проверяем, что курс USD -> RUB
        if rate.from_currency.code != "USD" or rate.to_currency.code != "RUB":
            raise ValueError("Поддерживается только курс USD -> RUB")
