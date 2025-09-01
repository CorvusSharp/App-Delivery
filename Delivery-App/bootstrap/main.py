"""
Точка входа приложения (uvicorn).
Инициализация DI, FastAPI, роутов, middleware.
"""
import uvicorn
from core.config import get_settings
from infrastructure.logging.config import setup_logging
from presentation.fastapi import create_app


def main() -> None:
    """Основная функция запуска приложения."""
    settings = get_settings()
    
    # Настройка логирования
    setup_logging(settings.DEBUG)
    

    # Запуск сервера
    uvicorn.run(
        "bootstrap.asgi:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        access_log=True,
        log_config=None,  # Используем наше собственное логирование
    )


if __name__ == "__main__":
    main()
