"""
Middleware для логирования запросов.
"""
import time
from typing import Callable
from fastapi import Request, Response
from loguru import logger


async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware для логирования HTTP запросов.
    
    Логирует информацию о входящих запросах и их обработке.
    """
    start_time = time.time()
    
    # Логируем входящий запрос
    logger.info(
        f"Входящий запрос: {request.method} {request.url.path} | "
        f"Query: {dict(request.query_params)} | "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    # Обрабатываем запрос
    response = await call_next(request)
    
    # Вычисляем время обработки
    process_time = time.time() - start_time
    
    # Логируем ответ
    logger.info(
        f"Ответ: {request.method} {request.url.path} | "
        f"Status: {response.status_code} | "
        f"Time: {process_time:.3f}s"
    )
    
    # Добавляем заголовок с временем обработки
    response.headers["X-Process-Time"] = str(process_time)
    
    return response
