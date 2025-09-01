"""
ASGI-приложение для prod/uvicorn/gunicorn.
"""
from presentation.fastapi import create_app

# Создание приложения для ASGI серверов
app = create_app()

