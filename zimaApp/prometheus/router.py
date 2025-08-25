import time
from random import random

from starlette.responses import PlainTextResponse

# from zimaApp.tasks.rabbitmq.consumer import start_consumer
from zimaApp.tasks.tasks import check_emails, check_emails_async, check_emails_for_excel, work_with_excel_summary
from prometheus_client import Counter, generate_latest
from fastapi import APIRouter, HTTPException, Depends


from zimaApp.config import settings
from redis import asyncio as aioredis

from zimaApp.logger import logger
from zimaApp.tasks.telegram_bot_template import TelegramInfo
from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users

router = APIRouter(
    prefix="/prometheus", tags=["Тестирование Grafana + Prometheus + redis + logger"]
)


# Метрика для подсчета успешных вызовов
logger_send_success_counter = Counter(
    'logger_send_success_total', 'Total successful calls to /logger_send'
)

# Метрика для подсчета ошибок
logger_send_error_counter = Counter(
    'logger_send_error_total', 'Total errors in /logger_send'
)


@router.get("/get_error")
def get_error():
    try:
        # Ваш код, который может вызвать исключение
        1 / 0  # Пример деления на ноль
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")


@router.get("/time_consumer")
def time_consumer():
    time.sleep(random() * 5)
    return 1


#
@router.get("/run-check-emails")
async def run_check_emails():
    # result = await start_consumer()
    result = await check_emails_async()
    return result

@router.get("/memory_consumer")
def memory_consumer():
    _ = [i for i in range(30_000_000)]
    return 1


@router.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest())

@router.post("/logger_send")
async def logger_send(message: dict, user: Users = Depends(get_current_user)):
    try:
        if user.login_user != 'Зуфаров И.М.':
            await TelegramInfo.send_message_logger(message)
            # Увеличиваем счетчик успешных вызовов
            logger_send_success_counter.inc()
    except Exception as e:
        # Увеличиваем счетчик ошибок
        logger_send_error_counter.inc()
        logger.error(e)


@router.get("/redis/ping")
async def redis_ping():
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8"
    )
    try:
        # Проверка соединения с Redis
        pong = await redis.ping()
        return {"status": "ok", "redis": pong}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")


@router.get("/redis/set")
async def redis_set(key: str, value: str):
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8"
    )
    try:
        await redis.set(key, value)
        return {"status": "success", "message": f"Key '{key}' set to '{value}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")


@router.get("/redis/get")
async def redis_get(key: str):
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8"
    )
    try:
        value = await redis.get(key)
        if value is None:
            return {"status": "not_found", "key": key}
        return {"status": "success", "key": key, "value": value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")

@router.post("/check_emails_and_upload")
async def check_emails_and_process(user: Users = Depends(get_current_user)):
    files_data = check_emails_for_excel()

    for file_data in files_data:
        well_data = await work_with_excel_summary(file_data["filename"], file_data["dataframe"])
        if well_data:
            try:
                logger.info(f"сводка по скважине {well_data.well_number} обновлена")
            except:
                logger.error(well_data)
    return {
        "found_files": [file['filename'] for file in files_data],
        "count": len(files_data)
    }
