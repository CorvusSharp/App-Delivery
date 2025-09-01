"""
Middleware для обработки ошибок приложения.
"""
import traceback
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

from core.exceptions import AppError, ValidationError, NotFoundError, ExternalServiceError


async def error_handling_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware для обработки ошибок приложения.
    
    Перехватывает исключения и преобразует их в стандартизированные JSON ответы.
    """
    try:
        response = await call_next(request)
        return response
        
    except HTTPException:
        # HTTPException уже обработаны FastAPI, пропускаем
        raise
        
    except ValidationError as e:
        logger.warning(f"Ошибка валидации: {e.message} | Детали: {e.details}")
        return JSONResponse(
            status_code=400,
            content={
                "error": True,
                "message": e.message,
                "error_code": e.error_code,
                "details": e.details
            }
        )
        
    except NotFoundError as e:
        logger.info(f"Ресурс не найден: {e.message}")
        return JSONResponse(
            status_code=404,
            content={
                "error": True,
                "message": e.message,
                "error_code": e.error_code,
                "details": e.details
            }
        )
        
    except ExternalServiceError as e:
        logger.error(f"Ошибка внешнего сервиса: {e.message} | Детали: {e.details}")
        return JSONResponse(
            status_code=502,
            content={
                "error": True,
                "message": "Ошибка внешнего сервиса",
                "error_code": e.error_code,
                "details": {"service": e.details.get("service_name", "unknown")}
            }
        )
        
    except AppError as e:
        logger.error(f"Ошибка приложения: {e.message} | Детали: {e.details}")
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": e.message,
                "error_code": e.error_code,
                "details": e.details
            }
        )
        
    except Exception as e:
        # Неожиданная ошибка
        logger.error(f"Неожиданная ошибка: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Внутренняя ошибка сервера",
                "error_code": "INTERNAL_ERROR",
                "details": {}
            }
        )
