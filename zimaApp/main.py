import asyncio
import time

import telegram
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_versioning import VersionedFastAPI

from prometheus_fastapi_instrumentator import Instrumentator
from redis import asyncio as aioredis
from sqladmin import Admin
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse, RedirectResponse
from starlette.staticfiles import StaticFiles

from zimaApp.admin.auth import authentication_backend
from zimaApp.admin.views import (
    ClassifierAdmin,
    RepairDataAdmin,
    SilencingAdmin,
    UserAdmin,
    WellsDataAdmin,
    NormsAdmin,
    GnktAdmin,
)
from zimaApp.config import settings, router_broker

from zimaApp.database import engine, init_mongo
from hawk_python_sdk.modules.fastapi import HawkFastapi

from zimaApp.files.dao import MongoFile
from zimaApp.tasks.rabbitmq.consumer import start_consumer
from zimaApp.tasks.tasks import check_emails, check_emails_async
from zimaApp.users.auth import authenticate_user
from zimaApp.users.router import router as user_router
from zimaApp.well_classifier.router import router as classifier_router
from zimaApp.well_silencing.router import router as silencing_router
from zimaApp.wells_repair_data.router import router as wells_repair_router
from zimaApp.brigade.router import router as brigade_router
from zimaApp.norms.router import router as norms_router
from zimaApp.gnkt_data.router import router as gnkt_router
from zimaApp.files.router import router as files_router
from zimaApp.wells_data.router import router as wells_data_router
from zimaApp.repairGis.router import router as repair_gis_router
from zimaApp.prometheus.router import router as prometheus_router
from zimaApp.pages.router import router as pages_router, templates
from zimaApp.logger import logger

bot = telegram.Bot(token=settings.TOKEN)
bot_user = telegram.Bot(token=settings.TOKEN_USERS)

client_mongo = MongoFile()

@asynccontextmanager
async def lifespan(_: FastAPI):
    # Получаем текущий активный цикл
    loop = asyncio.get_running_loop()

    # Запускаем потребителя как фоновую задачу в текущем цикле
    consumer_task = loop.create_task(start_consumer())

    # Инициализация MongoDB
    await init_mongo(client_mongo.client)

    try:
        print("Запуск приложения")
        redis = aioredis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8"
        )
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    except Exception as e:
        print(f"Ошибка при инициализации: {e}")

    try:
        if settings.MODE == "PROD":
            logger.info("Брокер стартовал")
            await bot.send_message(chat_id=settings.CHAT_ID, text="Приложение запущено")
            await bot_user.send_message(
                chat_id=settings.CHAT_ID, text="Приложение запущено!!!"
            )
            logger.info("Сообщение отправлено успешно")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

    yield  # Передача управления приложению

    # При завершении работы отменяем задачу потребителя
    if consumer_task:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            print("Потребитель остановлен")

    print("Завершение работы приложения")


app = FastAPI(lifespan=lifespan, title="Zima", version="0.1.0", root_path="")

# Подключение версионирования
vapp = VersionedFastAPI(
    app,
    version_format="{major}",
    prefix_format="/v{major}",
    description="Zima API",
    middleware=[
        Middleware(SessionMiddleware, secret_key=settings.SESSION_COOKIE_SECRET)
    ],
)

# Подключение статических файлов (JS, CSS)
try:
    app.mount("/static", StaticFiles(directory="zimaApp/static"), name="static")
except Exception as e:
    app.mount("/static", StaticFiles(directory="static"), name="static")

if settings.MODE != "TEST":
    hawk = HawkFastapi(
        {"app_instance": app, "token": settings.HAWK_DSN, "templates": templates}
    )


@app.get("/")
async def root():
    return RedirectResponse(url="/pages/home")


# Подключение эндпоинта для отображения метрик для их дальнейшего сбора Прометеусом
instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)
instrumentator.instrument(app).expose(app)


# Обработка ошибок валидации
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    invalid_params = []

    for err in errors:
        loc = err.get("loc", [])
        msg = err.get("msg", "")
        # Обычно loc содержит ['body', 'parameter_name']
        if len(loc) > 1:
            param_name = loc[-1]
        else:
            param_name = loc[0] if loc else "unknown"
        invalid_params.append({param_name: msg})

    logger.error(f"validation_exception: {errors}, body: {invalid_params}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": errors,
            "invalid_params": invalid_params,
            "body": exc.body,
            "message": "validation exception",
        },
    )


app.include_router(user_router)
app.include_router(wells_data_router)
app.include_router(wells_repair_router)
app.include_router(repair_gis_router)
app.include_router(brigade_router)
app.include_router(norms_router)
app.include_router(classifier_router)
app.include_router(silencing_router)
app.include_router(gnkt_router)
app.include_router(files_router)
app.include_router(prometheus_router)
app.include_router(pages_router)

# Подключение CORS, чтобы запросы к API могли приходить из браузера
origins = [
    "http://localhost:3000",
    "http://176.109.106.199:8000",
    "http://176.109.106.199:7777",
    "http://176.109.106.199:80",
    "http://127.0.0.1:8000",
    "http://83.174.202.38:8000",
    "http://83.174.202.38:7777",
    "http://83.174.202.38:80",
    "http://83.174.202.38:5555",
]
#
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)

if settings.MODE == "TEST":
    # При тестировании через pytest, необходимо подключать Redis, чтобы кэширование работало.
    # Иначе декоратор @cache из библиотеки fastapi-cache ломает выполнение кэшируемых эндпоинтов.
    # Из этого следует вывод, что сторонние решения порой ломают наш код, и это бывает проблематично поправить.
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf8",
        decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis), prefix="cache")

admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UserAdmin)
admin.add_view(WellsDataAdmin)
admin.add_view(SilencingAdmin)
admin.add_view(NormsAdmin)
admin.add_view(ClassifierAdmin)
admin.add_view(RepairDataAdmin)
admin.add_view(GnktAdmin)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(
            "request handling time", extra={"process_time": round(process_time, 4)}
        )

        return response
    except HTTPException as e:  # Обрабатываем исключения от endpoint
        process_time = time.time() - start_time
        response = e  # Или создайте новый Response
        response.headers["X-Process-Time"] = str(
            process_time
        )  # Важно: добавляем заголовок даже при ошибке
        return response

    except Exception as e:
        # Логируйте ошибку! Используйте модуль logging
        print(f"Unexpected error in middleware: {e}")
        process_time = time.time() - start_time
        response = Response(status_code=500, content=f"Internal Server Error: {e}")
        response.headers["X-Process-Time"] = str(
            process_time
        )  # Важно: добавляем заголовок даже при ошибке
        return response


if __name__ == "__main__":
    uvicorn.run("zimaApp.main:app", host="127.0.0.1", port=8000, reload=True)
