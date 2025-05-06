from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import date
from typing import Optional

import uvicorn
from fastapi import Depends, FastAPI, Query
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_versioning import VersionedFastAPI
from fastapi_cache.decorator import cache
from pydantic import BaseModel, json
from redis import asyncio as aioredis
from sqladmin import Admin, ModelView
from starlette.middleware.cors import CORSMiddleware

from zimaApp.admin.auth import authentication_backend
from zimaApp.admin.views import (
    ClassifierAdmin,
    RepairDataAdmin,
    SilencingAdmin,
    UserAdmin,
)
from zimaApp.config import settings
from zimaApp.database import engine
from zimaApp.users.models import Users
from zimaApp.users.router import router as user_router
from zimaApp.well_classifier.router import router as classifier_router
from zimaApp.well_silencing.router import router as silencing_router
from zimaApp.wells_repair_data.router import router as wells_repair_router

app = FastAPI(title="Zima", version="0.1.0", root_path="/zimaApp")

app.include_router(user_router)
app.include_router(wells_repair_router)
app.include_router(classifier_router)
app.include_router(silencing_router)

# Подключение CORS, чтобы запросы к API могли приходить из браузера
origins = [
    # 3000 - порт, на котором работает фронтенд на React.js
    "http://localhost:3000",
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

#
# # Подключение версионирования
# app = VersionedFastAPI(app,
#                        version_format='{major}',
#                        prefix_format='/api/v{major}',
#                        )


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield


admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UserAdmin)
admin.add_view(SilencingAdmin)
admin.add_view(ClassifierAdmin)
admin.add_view(RepairDataAdmin)

#
# @cache()
# async def get_cache():
#     return 1
#
#
# @cache(expire=60)
# async def index():
#     return dict(hello="world")


# class SRepairData(BaseModel):
#     well_number: str
#     area_well: str
#     well_oilfield: str
#     appointment:str
#     inv_number:str
#     wellhead_fittings:str
#     data_well: json
#     excel_json: json
#     contractor: str
#     costumer: str
#     work_plan: str
#     geolog: str
#     type_kr: str
#     data_change_paragraph: json
#     cdng: str
#     category_dict: json
#     angle_data: json
#     today: date


# @app.post("/repair_data")
# async def add_repair_data(repair_datas: SRepairData):
#     return pass

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
