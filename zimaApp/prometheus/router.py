import time
from random import random

from fastapi import APIRouter, HTTPException, Depends
from fastapi_cache import FastAPICache

from zimaApp.config import settings
from redis import asyncio as aioredis

from zimaApp.logger import logger
from zimaApp.tasks.telegram_bot_template import TelegramInfo
from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users

router = APIRouter(
    prefix="/prometheus",
    tags=["Тестирование Grafana + Prometheus + redis + logger"]
)


@router.get("/get_error")
def get_error():
    try:
        # Ваш код, который может вызвать исключение
        1 / 0  # Пример деления на ноль
    except Exception as e:
        logger.error(f'Произошла ошибка: {e}')


@router.get("/time_consumer")
def time_consumer():
    time.sleep(random() * 5)
    return 1


@router.get("/memory_consumer")
def memory_consumer():
    _ = [i for i in range(30_000_000)]
    return 1


@router.post("/logger_send")
async def logger_send(message: dict):
    try:
        await TelegramInfo.send_message_logger(message)
    except Exception as e:
        logger.error(e)

@router.get("/redis/ping")
async def redis_ping():
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8")
    try:
        # Проверка соединения с Redis
        pong = await redis.ping()
        return {"status": "ok", "redis": pong}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")


@router.get("/redis/set")
async def redis_set(key: str, value: str):
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8")
    try:
        await redis.set(key, value)
        return {"status": "success", "message": f"Key '{key}' set to '{value}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")


@router.get("/redis/get")
async def redis_get(key: str):
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8")
    try:
        value = await redis.get(key)
        if value is None:
            return {"status": "not_found", "key": key}
        return {"status": "success", "key": key, "value": value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")
