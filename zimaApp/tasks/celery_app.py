from celery import Celery

from zimaApp.config import settings

celery_app = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    include=["zimaApp.tasks.tasks"],
)
