"""
ORM-модели для SQLAlchemy.
Package, PackageType, индексы, связи, default-ы.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from infrastructure.sqlalchemy.database import Base


class PackageTypeModel(Base):
    """ORM модель типа посылки."""
    __tablename__ = "package_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    
    # Связь с посылками
    packages = relationship("PackageModel", back_populates="package_type")


class PackageModel(Base):
    """ORM модель посылки."""
    __tablename__ = "packages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    weight = Column(Numeric(10, 3), nullable=False)  # килограммы с точностью до грамма
    value_usd = Column(Numeric(12, 2), nullable=False)  # доллары с центами
    session_id = Column(String(36), nullable=False, index=True)  # UUID
    delivery_price_rub = Column(Numeric(12, 2), nullable=True)  # рубли с копейками
    
    # Внешний ключ
    type_id = Column(Integer, ForeignKey("package_types.id"), nullable=False, index=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Связи
    package_type = relationship("PackageTypeModel", back_populates="packages")
    
    # Индексы для оптимизации запросов
    __table_args__ = (
        Index("ix_packages_session_type", "session_id", "type_id"),
        Index("ix_packages_session_price", "session_id", "delivery_price_rub"),
        Index("ix_packages_no_price", "delivery_price_rub"),  # для поиска без цены
        Index("ix_packages_created", "created_at"),
    )
