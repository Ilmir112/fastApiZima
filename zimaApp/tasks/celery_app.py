from celery import Celery

from zimaApp.config import settings

celery_app = Celery(
    "tasks",
    broker=settings.rabbitmq_url,
    backend="rpc://",
    include=["zimaApp.tasks.tasks"],
)

# celery_app = Celery(
#     "tasks",
#     broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
#     include=["zimaApp.tasks.tasks"],
# )

celery_app.conf.beat_schedule = {
    "check-emails-every-2-minutes": {
        "task": "tasks.check_emails_async",
        "schedule": 600,  # интервал в секундах (10 минуты)
    },
    "check-emails-for-excel-every-hour": {
        "task": "tasks.check_emails_summary",
        "schedule": 43200,  # интервал в секундах (1 час)
    },
}
celery_app.conf.timezone = "Asia/Yekaterinburg"
