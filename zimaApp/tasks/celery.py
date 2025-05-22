from celery import Celery

from zimaApp.config import settings

celery = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    include=["zimaApp.tasks.tasks"],
)
