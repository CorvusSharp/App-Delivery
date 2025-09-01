"""Create package_types and packages tables

Revision ID: 001
Revises: 
Create Date: 2025-08-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Index


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создание таблицы package_types
    op.create_table(
        'package_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Создание индекса для package_types
    op.create_index('ix_package_types_id', 'package_types', ['id'])
    op.create_index('ix_package_types_name', 'package_types', ['name'])
    
    # Создание таблицы packages
    op.create_table(
        'packages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('weight', sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column('value_usd', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('delivery_price_rub', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('type_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['type_id'], ['package_types.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создание индексов для packages
    op.create_index('ix_packages_id', 'packages', ['id'])
    op.create_index('ix_packages_session_id', 'packages', ['session_id'])
    op.create_index('ix_packages_type_id', 'packages', ['type_id'])
    op.create_index('ix_packages_created', 'packages', ['created_at'])
    
    # Композитные индексы для оптимизации запросов
    op.create_index('ix_packages_session_type', 'packages', ['session_id', 'type_id'])
    op.create_index('ix_packages_session_price', 'packages', ['session_id', 'delivery_price_rub'])
    op.create_index('ix_packages_no_price', 'packages', ['delivery_price_rub'])


def downgrade() -> None:
    # Удаление индексов packages
    op.drop_index('ix_packages_no_price', table_name='packages')
    op.drop_index('ix_packages_session_price', table_name='packages')
    op.drop_index('ix_packages_session_type', table_name='packages')
    op.drop_index('ix_packages_created', table_name='packages')
    op.drop_index('ix_packages_type_id', table_name='packages')
    op.drop_index('ix_packages_session_id', table_name='packages')
    op.drop_index('ix_packages_id', table_name='packages')
    
    # Удаление таблицы packages
    op.drop_table('packages')
    
    # Удаление индексов package_types
    op.drop_index('ix_package_types_name', table_name='package_types')
    op.drop_index('ix_package_types_id', table_name='package_types')
    
    # Удаление таблицы package_types
    op.drop_table('package_types')
