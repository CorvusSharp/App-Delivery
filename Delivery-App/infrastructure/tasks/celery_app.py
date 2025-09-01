"""
Конфигурация Celery приложения.
"""
from celery import Celery
from celery.schedules import crontab

from core.config import get_settings

settings = get_settings()

# Создание Celery приложения
celery_app = Celery(
    "delivery_app",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "infrastructure.tasks.currency_tasks",
        "infrastructure.tasks.delivery_tasks"
    ]
)

# Конфигурация Celery
celery_app.conf.update(
    # Настройки задач
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Настройки worker'а
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    # Включаем события/статусы для Flower
    worker_send_task_events=True,
    task_track_started=True,
    
    # Настройки результатов
    result_expires=3600,  # 1 час
    # Отправлять событие "task-sent" при публикации задач
    task_send_sent_event=True,
    
    # Маршрутизация задач по очередям
    task_routes={
        "infrastructure.tasks.delivery_tasks.calculate_package_price": {"queue": "pricing"},
        "infrastructure.tasks.delivery_tasks.calculate_delivery_prices": {"queue": "pricing-bulk"},
        "infrastructure.tasks.currency_tasks.update_currency_rates": {"queue": "ops"},
        "infrastructure.tasks.delivery_tasks.cleanup_expired_sessions": {"queue": "ops"},
        "infrastructure.tasks.delivery_tasks.get_packages_without_price_count": {"queue": "ops"},
    },

    # Расписание периодических задач
    beat_schedule={
        "update-currency-rates": {
            "task": "infrastructure.tasks.currency_tasks.update_currency_rates",
            "schedule": crontab(minute="*/5"),  # Каждые 5 минут
        },
        # Редкий catch-up расчёт (страховка): раз в час
        "calculate-delivery-prices-catchup": {
            "task": "infrastructure.tasks.delivery_tasks.calculate_delivery_prices",
            "schedule": crontab(minute=0),  # Каждый час в начале часа
        },
        "cleanup-expired-sessions": {
            "task": "infrastructure.tasks.delivery_tasks.cleanup_expired_sessions",
            "schedule": crontab(hour=3, minute=0),  # Ежедневно в 03:00 UTC
        },
    },
)


@celery_app.task(bind=True)
def debug_task(self):
    """Отладочная задача."""
    print(f'Request: {self.request!r}')
