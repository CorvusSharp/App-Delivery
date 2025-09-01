"""
Реализация репозитория посылок на SQLAlchemy.
"""
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.entities.package import Package
from domain.ports.package_repository import PackageRepository
from domain.value_objects.identifiers import PackageId, SessionId
from infrastructure.sqlalchemy.models import PackageModel


class SQLAlchemyPackageRepository(PackageRepository):
    """Реализация репозитория посылок на SQLAlchemy."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, package: Package) -> Package:
        """Сохранить посылку."""
        if package.id.value == 0:
            # Создание новой посылки
            db_package = PackageModel(
                name=package.name,
                weight=package.weight,
                type_id=package.type_id,
                value_usd=package.value_usd,
                session_id=package.session_id,
                delivery_price_rub=package.delivery_price_rub
            )
            self.session.add(db_package)
            await self.session.flush()
            await self.session.refresh(db_package)
            await self.session.commit()
            
            # Обновляем доменную сущность с новым ID
            package.id = PackageId.from_int(db_package.id)
            package.created_at = db_package.created_at
            package.updated_at = db_package.updated_at
            
        else:
            # Обновление существующей посылки
            stmt = select(PackageModel).where(PackageModel.id == package.id.value)
            result = await self.session.execute(stmt)
            db_package = result.scalar_one_or_none()
            
            if not db_package:
                raise ValueError(f"Посылка с ID {package.id.value} не найдена")
            
            # Обновляем поля
            db_package.name = package.name
            db_package.weight = package.weight
            db_package.type_id = package.type_id
            db_package.value_usd = package.value_usd
            db_package.delivery_price_rub = package.delivery_price_rub
            
            await self.session.flush()
            await self.session.refresh(db_package)
            await self.session.commit()
            
            package.updated_at = db_package.updated_at
        
        return package
    
    async def get_by_id(self, package_id: PackageId) -> Optional[Package]:
        """Получить посылку по ID."""
        stmt = (
            select(PackageModel)
            .options(selectinload(PackageModel.package_type))
            .where(PackageModel.id == package_id.value)
        )
        result = await self.session.execute(stmt)
        db_package = result.scalar_one_or_none()
        
        if not db_package:
            return None
        
        return self._to_domain_entity(db_package)
    
    async def get_by_session_id(
        self,
        session_id: SessionId,
        type_id: Optional[int] = None,
        has_price: Optional[bool] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[Package]:
        """Получить посылки по session_id с фильтрами и пагинацией."""
        stmt = (
            select(PackageModel)
            .options(selectinload(PackageModel.package_type))
            .where(PackageModel.session_id == session_id.value)
        )
        
        # Применяем фильтры
        if type_id is not None:
            stmt = stmt.where(PackageModel.type_id == type_id)
        
        if has_price is not None:
            if has_price:
                stmt = stmt.where(PackageModel.delivery_price_rub.is_not(None))
            else:
                stmt = stmt.where(PackageModel.delivery_price_rub.is_(None))
        
        # Пагинация и сортировка
        stmt = stmt.order_by(PackageModel.created_at.desc())
        stmt = stmt.offset(offset).limit(limit)
        
        result = await self.session.execute(stmt)
        db_packages = result.scalars().all()
        
        return [self._to_domain_entity(db_package) for db_package in db_packages]
    
    async def count_by_session_id(
        self,
        session_id: SessionId,
        type_id: Optional[int] = None,
        has_price: Optional[bool] = None
    ) -> int:
        """Подсчитать количество посылок по session_id с фильтрами."""
        stmt = (
            select(func.count(PackageModel.id))
            .where(PackageModel.session_id == session_id.value)
        )
        
        # Применяем фильтры
        if type_id is not None:
            stmt = stmt.where(PackageModel.type_id == type_id)
        
        if has_price is not None:
            if has_price:
                stmt = stmt.where(PackageModel.delivery_price_rub.is_not(None))
            else:
                stmt = stmt.where(PackageModel.delivery_price_rub.is_(None))
        
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def get_packages_without_price(self, limit: int = 100) -> List[Package]:
        """Получить посылки без рассчитанной цены доставки."""
        stmt = (
            select(PackageModel)
            .options(selectinload(PackageModel.package_type))
            .where(PackageModel.delivery_price_rub.is_(None))
            .order_by(PackageModel.created_at.asc())
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        db_packages = result.scalars().all()
        
        return [self._to_domain_entity(db_package) for db_package in db_packages]
    
    async def update_delivery_prices(self, prices: dict[int, float]) -> int:
        """
        Обновить цены доставки для нескольких посылок.
        
        Args:
            prices: Словарь {package_id: delivery_price_rub}
            
        Returns:
            Количество обновленных записей
        """
        if not prices:
            return 0
        
        updated_count = 0
        
        for package_id, price in prices.items():
            stmt = (
                select(PackageModel)
                .where(PackageModel.id == package_id)
            )
            result = await self.session.execute(stmt)
            db_package = result.scalar_one_or_none()
            
            if db_package:
                db_package.delivery_price_rub = price
                updated_count += 1
        
        if updated_count:
            await self.session.commit()
        return updated_count
    
    def _to_domain_entity(self, db_package: PackageModel) -> Package:
        """Конвертировать ORM модель в доменную сущность."""
        return Package(
            id=PackageId.from_int(db_package.id),
            name=db_package.name,
            weight=db_package.weight,
            type_id=db_package.type_id,
            value_usd=db_package.value_usd,
            session_id=db_package.session_id,
            delivery_price_rub=db_package.delivery_price_rub,
            created_at=db_package.created_at,
            updated_at=db_package.updated_at
        )
