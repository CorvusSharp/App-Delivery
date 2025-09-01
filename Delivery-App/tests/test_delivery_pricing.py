from decimal import Decimal

from domain.entities.package import Package
from domain.services.delivery_pricing import DeliveryPricingService
from domain.value_objects.currency import Rate
from domain.value_objects.identifiers import PackageId


def test_calculate_delivery_price_basic():
    svc = DeliveryPricingService()
    pkg = Package(
        id=PackageId.from_int(1),
        name="Test",
        weight=Decimal("2.000"),
        type_id=1,
        value_usd=Decimal("100.00"),
        session_id="00000000-0000-0000-0000-000000000000",
    )
    rate = Rate.usd_to_rub(Decimal("90.00"))

    price = svc.calculate_delivery_price(pkg, rate)

    # (2 * 0.5 + 100 * 0.01) * 90 = (1 + 1) * 90 = 180.00
    assert price == Decimal("180.00")
