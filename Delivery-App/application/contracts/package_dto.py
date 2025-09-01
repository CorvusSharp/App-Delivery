"""
Контракты UC для работы с посылками (Pydantic v2).
"""
from decimal import Decimal
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, computed_field


class CreatePackageDTO(BaseModel):
    """Данные для создания посылки."""
    name: str
    weight: Decimal
    type_id: int
    value_usd: Decimal
    session_id: str


class PackageDTO(BaseModel):
    """Данные посылки."""
    id: int
    name: str
    weight: Decimal
    type_id: int
    value_usd: Decimal
    session_id: str
    delivery_price_rub: Optional[Decimal] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    type_name: Optional[str] = Field(default=None)

    @computed_field  # type: ignore[misc]
    @property
    def has_calculated_price(self) -> bool:
        return self.delivery_price_rub is not None

    @computed_field  # type: ignore[misc]
    @property
    def status(self) -> str:
        return "calculated" if self.has_calculated_price else "pending"


class PackageListItemDTO(BaseModel):
    """Элемент списка посылок."""
    id: int
    name: str
    weight: Decimal
    type_id: int
    type_name: str
    value_usd: Decimal
    delivery_price_rub: Optional[Decimal] = Field(default=None)
    status: str
    created_at: Optional[datetime] = Field(default=None)


class PackageFilterDTO(BaseModel):
    """Фильтры поиска посылок."""
    session_id: str
    type_id: Optional[int] = Field(default=None)
    has_price: Optional[bool] = Field(default=None)
    offset: int = Field(default=0)
    limit: int = Field(default=100)
