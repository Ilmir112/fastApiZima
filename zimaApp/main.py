import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_versioning import VersionedFastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from redis import asyncio as aioredis
from sqladmin import Admin
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from zimaApp.admin.auth import authentication_backend
from zimaApp.admin.views import (
    ClassifierAdmin,
    RepairDataAdmin,
    SilencingAdmin,
    UserAdmin, WellsDataAdmin,
)
from zimaApp.config import settings
from zimaApp.database import engine
from hawk_python_sdk.modules.fastapi import HawkFastapi
from zimaApp.users.router import router as user_router
from zimaApp.well_classifier.router import router as classifier_router
from zimaApp.well_silencing.router import router as silencing_router
from zimaApp.wells_repair_data.router import router as wells_repair_router
from zimaApp.gnkt_data.router import router as gnkt_router
from zimaApp.wells_data.router import router as wells_data_router
from zimaApp.prometheus import router as prometheus_router
from zimaApp.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8",
                              decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")


app = FastAPI(lifespan=lifespan, title="Zima", version="0.1.0", root_path="/zimaApp")

if settings.MODE != "TEST":
    hawk = HawkFastapi({
        'app_instance': app,
        'token': settings.HAWK_DSN
    })

# Подключение эндпоинта для отображения метрик для их дальнейшего сбора Прометеусом
instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)
instrumentator.instrument(app).expose(app)


# Обработка ошибок валидации
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"validation_exception: {exc.errors()}, body: {exc.body}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": exc.body,
            "message": "validation xception"
        },
    )


app.include_router(user_router)
app.include_router(wells_data_router)
app.include_router(wells_repair_router)
app.include_router(classifier_router)
app.include_router(silencing_router)
app.include_router(gnkt_router)
app.include_router(prometheus_router)

# Подключение CORS, чтобы запросы к API могли приходить из браузера
origins = [
    "https://fastapizima.onrender.com",
    "http://localhost:3000",
    "http://127.0.0.1:8000",  # для локальной разработки
]

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

# Подключение версионирования
app = VersionedFastAPI(app,
                       version_format='{major}',
                       prefix_format='/api/v{major}',
                       )

if settings.MODE == "TEST":
    # При тестировании через pytest, необходимо подключать Redis, чтобы кэширование работало.
    # Иначе декоратор @cache из библиотеки fastapi-cache ломает выполнение кэшируемых эндпоинтов.
    # Из этого следует вывод, что сторонние решения порой ломают наш код, и это бывает проблематично поправить.
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8",
                              decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")

admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UserAdmin)
admin.add_view(WellsDataAdmin)
admin.add_view(SilencingAdmin)
admin.add_view(ClassifierAdmin)
admin.add_view(RepairDataAdmin)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    # response.headers["X-Process-Time"] = str(process_time)
    # logger.info("request handling time",
    #             extra={
    #                 "process_time": round(process_time, 4)
    #             })
    return response


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
