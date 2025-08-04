
import mimetypes
from datetime import datetime
from bson import ObjectId
from fastapi import UploadFile

from motor.motor_asyncio import AsyncIOMotorGridFSBucket, AsyncIOMotorClient
from zimaApp.config import settings
from zimaApp.database import ImageMongoDB  # предполагаю, что это модель/схема
from zimaApp.logger import logger



class MongoFile:

    @classmethod
    async def upload_file(cls, itemId: str, file: UploadFile, fs):
        try:
            filename = file.filename
            contents = await file.read()

            # Определяем MIME тип
            mime_type, _ = mimetypes.guess_type(filename)
            content_type = mime_type or "application/octet-stream"

            # Загружаем содержимое в GridFS
            gridfs_id = await fs.upload_from_stream(
                filename,
                contents,
                metadata={
                    "contentType": content_type,
                    "field_id": itemId,
                    "upload_date": datetime.utcnow(),
                    "size": len(contents),
                }
            )

            # Создайте экземпляр модели
            document = ImageMongoDB(
                name=filename,
                file_id=str(gridfs_id)  # добавьте ID файла в GridFS
            )

            # Вставляем документ в коллекцию (предположим, что у вас есть модель)
            result = await ImageMongoDB.insert_one(document)
            file_id_str = str(result.id)

            # Формируем ссылку на файл (может быть API для скачивания по ID)
            file_url = f"/files/{file_id_str}"

            return file_url, file_id_str, filename
        except Exception as e:
            logger.error(e)

    @classmethod
    async def get_file_from_mongo(cls, file_id: str, fs):
        try:
            # Получаем документ по ID
            doc = await ImageMongoDB.find_one({"_id": ObjectId(file_id)})
            if not doc:
                raise Exception("Файл не найден")

            # Получаем file_id из документа
            gridfs_id = doc.file_id  # предполагается, что это поле есть и правильно заполнено
            if not gridfs_id:
                raise Exception("ID файла в GridFS отсутствует")

            # Если gridfs_id — строка, преобразуйте в ObjectId
            if isinstance(gridfs_id, str):
                gridfs_id = ObjectId(gridfs_id)

            # Открываем поток для скачивания
            stream = await fs.open_download_stream(gridfs_id)
            return stream  # Можно вернуть поток или прочитать полностью
        except Exception as e:
            logger.error(e)

    async def delete_file_from_mongo(self, file_id: str, fs):
        fs.delete(ObjectId(file_id))
        return True