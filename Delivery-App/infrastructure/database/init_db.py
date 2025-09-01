"""
Скрипт инициализации базы данных.
Заполняет таблицу package_types тремя типами посылок если они отсутствуют.
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую папку проекта в sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert

from infrastructure.sqlalchemy.database import AsyncSessionLocal
from domain.entities.package_type import PackageType
from infrastructure.sqlalchemy.models import PackageTypeModel


async def init_package_types():
    """Инициализировать типы посылок в базе данных."""
    
    # Получаем все доменные типы
    domain_types = PackageType.get_all_types()
    
    async with AsyncSessionLocal() as session:
        try:
            print("🔄 Проверяем существующие типы посылок...")
            
            # Проверяем, какие типы уже есть в БД
            existing_types_result = await session.execute(
                select(PackageTypeModel.id, PackageTypeModel.name)
            )
            existing_types = {row.id: row.name for row in existing_types_result}
            
            print(f"📋 Найдено существующих типов: {len(existing_types)}")
            for type_id, type_name in existing_types.items():
                print(f"   - {type_id}: {type_name}")
            
            # Вставляем отсутствующие типы
            types_to_insert = []
            for domain_type in domain_types:
                if domain_type.id not in existing_types:
                    types_to_insert.append({
                        'id': domain_type.id,
                        'name': domain_type.name
                    })
                    print(f"➕ Будет добавлен тип: {domain_type.id} - {domain_type.name}")
                else:
                    print(f"✅ Тип уже существует: {domain_type.id} - {domain_type.name}")
            
            if types_to_insert:
                # Используем PostgreSQL UPSERT (ON CONFLICT DO NOTHING)
                stmt = insert(PackageTypeModel).values(types_to_insert)
                stmt = stmt.on_conflict_do_nothing(index_elements=['id'])
                
                await session.execute(stmt)
                await session.commit()
                
                print(f"✅ Успешно добавлено {len(types_to_insert)} типов посылок")
            else:
                print("✅ Все типы посылок уже существуют в базе данных")
            
            # Проверяем финальное состояние
            final_result = await session.execute(
                select(PackageTypeModel.id, PackageTypeModel.name)
                .order_by(PackageTypeModel.id)
            )
            final_types = list(final_result)
            
            print(f"\n📊 Итоговое состояние типов посылок ({len(final_types)}):")
            for row in final_types:
                print(f"   - {row.id}: {row.name}")
                
        except Exception as e:
            print(f"❌ Ошибка при инициализации типов посылок: {e}")
            await session.rollback()
            raise


async def check_database_connection():
    """Проверить подключение к базе данных."""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            if result.scalar() == 1:
                print("✅ Подключение к базе данных успешно")
                return True
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return False
    
    return False


async def main():
    """Основная функция скрипта."""
    print("🚀 Запуск инициализации базы данных...")
    
    # Проверяем подключение
    if not await check_database_connection():
        print("❌ Не удалось подключиться к базе данных. Проверьте настройки.")
        sys.exit(1)
    
    try:
        # Инициализируем типы посылок
        await init_package_types()
        
        print("\n🎉 Инициализация базы данных завершена успешно!")
        
    except Exception as e:
        print(f"\n❌ Ошибка при инициализации: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
