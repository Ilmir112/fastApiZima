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
    field_id: str = Field(default="")  # или None, если нужно

    class Settings:
        name = "images_pdf"
        indexes = [
            pymongo.IndexModel([("name", pymongo.TEXT)])
        ]


async def init_mongo():
    try:
        client = AsyncIOMotorClient(settings.MONGO_DATABASE_URL)
        await init_beanie(database=client['images_pdf'], document_models=[ImageMongoDB])

        # Создаем или ищем документ
        images_pdf = await ImageMongoDB.find_one({"name": "zima_data"})
        if not images_pdf:
            images_pdf = ImageMongoDB(name="zima_data")
            await images_pdf.insert()

    except Exception as e:
        logger.info(str(e))