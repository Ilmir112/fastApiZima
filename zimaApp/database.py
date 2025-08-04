from datetime import datetime

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient


from zimaApp.config import settings
from zimaApp.logger import logger

if settings.MODE == "TEST":
    DATABASE_URL = settings.TEST_DATABASE_URL
    DATABASE_PARAMS = {"poolclass": NullPool}
else:
    DATABASE_URL = settings.DATABASE_URL
    DATABASE_PARAMS = {}

engine = create_async_engine(DATABASE_URL, **DATABASE_PARAMS, echo=False)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


from beanie import Document, init_beanie
from pydantic import Field
import pymongo


class ImageMongoDB(Document):
    name: str = Field(..., unique=True)
    file_id: str = Field(default="")


    class Settings:
        name = "files"
        indexes = [pymongo.IndexModel([("name", pymongo.TEXT)])]


async def init_mongo():
    try:
        client = AsyncIOMotorClient(settings.MONGO_DATABASE_URL)
        logger.info("попытка старта")
        await init_beanie(database=client["files"], document_models=[ImageMongoDB])
        logger.info("Монго стартовал")
        #
        # # Создаем или ищем документ
        # images_pdf = await ImageMongoDB.find_one({"name": "zima_data"})
        # if not images_pdf:
        #     new_image = ImageMongoDB(
        #         name='zima_data',
        #         file_data=b'...',  # байты файла
        #         content_type='image/jpeg',  # например
        #         size=1024  # размер файла в байтах
        #     )
        #     await images_pdf.insert()
        return client
    except Exception as e:
        logger.error(str(e))
