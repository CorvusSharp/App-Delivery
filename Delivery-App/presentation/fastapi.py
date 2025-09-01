"""
Создание и настройка FastAPI приложения.
Сборка FastAPI: роутеры, DI, OpenAPI/Swagger.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.logging.config import setup_logging, get_logger

from core.config import get_settings
from presentation.middleware import error_handling_middleware, logging_middleware


def create_app() -> FastAPI:
    """Создать и настроить FastAPI приложение."""
    settings = get_settings()
    
    # Создание приложения
    app = FastAPI(
        title=settings.APP_NAME,
        description="API для расчёта стоимости доставки посылок",
        version="1.0.0",
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
        openapi_url=settings.OPENAPI_URL,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Кастомные middleware (сначала логирование, затем обработка ошибок)
    app.middleware("http")(logging_middleware)
    app.middleware("http")(error_handling_middleware)
    
    # Подключение роутеров
    from presentation.routers import packages, package_types, delivery, health
    
    app.include_router(packages.router, prefix="/api/v1", tags=["packages"])
    app.include_router(package_types.router, prefix="/api/v1", tags=["package-types"])
    app.include_router(delivery.router, prefix="/api/v1", tags=["delivery"])
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    
    # События жизненного цикла
    @app.on_event("startup")
    async def startup_event():
        """Действия при запуске приложения."""
        # Настройка логирования
        setup_logging(debug=settings.DEBUG)
        logger = get_logger("startup")
        # Инициализация типов посылок
        from infrastructure.database.init_db import init_package_types
        try:
            await init_package_types()
        except Exception as e:
            logger.exception(f"Ошибка инициализации типов посылок: {e}")
    
    return app
