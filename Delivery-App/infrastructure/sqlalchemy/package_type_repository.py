"""
Реализация репозитория типов посылок на SQLAlchemy.
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.package_type import PackageType
from domain.ports.package_type_repository import PackageTypeRepository
from infrastructure.sqlalchemy.models import PackageTypeModel


class SQLAlchemyPackageTypeRepository(PackageTypeRepository):
    """Реализация репозитория типов посылок на SQLAlchemy."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, type_id: int) -> Optional[PackageType]:
        """Получить тип посылки по ID."""
        stmt = select(PackageTypeModel).where(PackageTypeModel.id == type_id)
        result = await self.session.execute(stmt)
        db_type = result.scalar_one_or_none()
        
        if not db_type:
            return None
        
        return self._to_domain_entity(db_type)
    
    async def get_all(self) -> List[PackageType]:
        """Получить все типы посылок."""
        stmt = select(PackageTypeModel).order_by(PackageTypeModel.id)
        result = await self.session.execute(stmt)
        db_types = result.scalars().all()
        
        return [self._to_domain_entity(db_type) for db_type in db_types]

    async def get_by_name(self, name: str) -> Optional[PackageType]:
        """Получить тип посылки по названию."""
        stmt = select(PackageTypeModel).where(PackageTypeModel.name == name)
        result = await self.session.execute(stmt)
        db_type = result.scalar_one_or_none()
        if not db_type:
            return None
        return self._to_domain_entity(db_type)
    
    async def exists(self, type_id: int) -> bool:
        """Проверить существование типа посылки."""
        stmt = select(PackageTypeModel.id).where(PackageTypeModel.id == type_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def save(self, package_type: PackageType) -> PackageType:
        """Сохранить тип посылки."""
        # Проверяем, существует ли уже
        existing = await self.get_by_id(package_type.id)
        
        if existing:
            # Обновляем существующий
            stmt = select(PackageTypeModel).where(PackageTypeModel.id == package_type.id)
            result = await self.session.execute(stmt)
            db_type = result.scalar_one()
            
            db_type.name = package_type.name
        else:
            # Создаем новый
            db_type = PackageTypeModel(
                id=package_type.id,
                name=package_type.name
            )
            self.session.add(db_type)
        
        await self.session.flush()
        return package_type
    
    def _to_domain_entity(self, db_type: PackageTypeModel) -> PackageType:
        """Конвертировать ORM модель в доменную сущность."""
        return PackageType(
            id=db_type.id,
            name=db_type.name
        )
