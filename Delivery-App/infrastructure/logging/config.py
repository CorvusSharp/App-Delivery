"""
Конфигурация логирования с использованием loguru.
Интеграция с uvicorn access логами.
"""
import sys
from pathlib import Path
from loguru import logger


def setup_logging(debug: bool = False) -> None:
    """Настроить логирование для приложения."""
    
    # Очистить стандартные handlers
    logger.remove()
    
    # Формат для логов
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Консольный вывод
    logger.add(
        sys.stderr,
        format=log_format,
        level="DEBUG" if debug else "INFO",
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    # Файловый вывод
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Основной лог
    logger.add(
        logs_dir / "app.log",
        format=log_format,
        level="DEBUG" if debug else "INFO",
        rotation="1 day",
        retention="30 days",
        compression="gz",
        backtrace=True,
        diagnose=True,
    )
    
    # Лог ошибок
    logger.add(
        logs_dir / "errors.log",
        format=log_format,
        level="ERROR",
        rotation="1 day",
        retention="30 days",
        compression="gz",
        backtrace=True,
        diagnose=True,
    )
    
    # Настройка уровня логирования для внешних библиотек
    if not debug:
        logger.disable("sqlalchemy.engine")


def get_logger(name: str) -> "logger":
    """Получить логгер с именем."""
    return logger.bind(name=name)


class InterceptHandler:
    """Handler для перехвата стандартных логов Python."""
    
    def emit(self, record):
        """Перенаправить лог в loguru."""
        # Получить соответствующий уровень Loguru
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        # Найти вызывающий фрейм
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == __file__:
            frame = frame.f_back
            depth += 1
        
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )
