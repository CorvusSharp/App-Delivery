"""Инициализация модуля infrastructure/tasks."""

from .celery_app import celery_app

__all__ = [
    "celery_app"
]
