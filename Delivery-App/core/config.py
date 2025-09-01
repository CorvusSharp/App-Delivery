# core/config.py
"""
Конфигурация приложения с использованием Pydantic Settings (v2).
Добавлены свойства для ASYNC/SYNC URL базы.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # === Основные ===
    APP_NAME: str = "Delivery App"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # === База данных ===
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "delivery_app"

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """
        Синхронный DSN (если когда-то понадобится). НЕ используется приложением/миграциями.
        """
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """
        Асинхронный DSN (используется приложением и alembic env.py).
        """
        # допускаем, что хост/порт/логин уже могут быть переопределены через переменные окружения
        # возвращаем URL на asyncpg:
        return self.SYNC_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

    # === Celery (RabbitMQ + RPC backend) ===
    CELERY_BROKER_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    CELERY_RESULT_BACKEND: str = "rpc://"

    # === CBR API ===
    CBR_API_URL: str = "https://www.cbr-xml-daily.ru/daily_json.js"
    CBR_TIMEOUT: int = 10
    CBR_RETRY_COUNT: int = 3

    # === Redis ===
    REDIS_URL: str | None = None  # пример: redis://redis:6379/0
    REDIS_DB_CACHE: int = 0
    REDIS_DB_SESSIONS: int = 1

    # === CORS ===
    # В .env хранится JSON-массив строк -> pydantic корректно распарсит
    # В продакшене ограничьте список доменов фронтенда
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # === Security ===
    SESSION_SECRET_KEY: str = "your-secret-key-change-in-production"
    SESSION_COOKIE_NAME: str = "delivery_session"
    SESSION_COOKIE_MAX_AGE: int = 86400 * 30  # 30 дней
    # Для продакшена рекомендуется True (HTTPS); в dev может быть False
    SESSION_COOKIE_SECURE: bool = False  # True для HTTPS
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "lax"

    # === Документация ===
    DOCS_URL: Optional[str] = "/docs"
    REDOC_URL: Optional[str] = "/redoc"
    OPENAPI_URL: Optional[str] = "/openapi.json"

    # Pydantic v2 Settings config
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # игнорируем лишние переменные окружения (например, REDIS_*)
    )


@lru_cache()
def get_settings() -> Settings:
    """Получить настройки приложения (с кэшированием)."""
    return Settings()
