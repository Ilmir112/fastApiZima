
import mimetypes
from datetime import datetime, timedelta
import re
from zoneinfo import ZoneInfo

from bson import ObjectId
from fastapi import UploadFile, Request

from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from zimaApp.database import ImageMongoDB  # предполагаю, что это модель/схема
from zimaApp.logger import logger


class MongoFile:
    @classmethod
    async def upload_file(cls, request: Request, itemId: str, file: UploadFile):
        try:
            db = request.app.state.mongo_client["files"]
            fs_bucket = AsyncIOMotorGridFSBucket(db)
            filename = file.filename
            contents = await file.read()

            # Определяем MIME тип
            mime_type, _ = mimetypes.guess_type(filename)
            content_type = mime_type or "application/octet-stream"

            # Загружаем содержимое в GridFS
            gridfs_id = await fs_bucket.upload_from_stream(
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
    async def get_file_from_mongo(cls, request: Request, file_id: str):
        try:
            db = request.app.state.mongo_client["files"]
            fs_bucket = AsyncIOMotorGridFSBucket(db)
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
            stream = await fs_bucket.open_download_stream(gridfs_id)
            return stream  # Можно вернуть поток или прочитать полностью
        except Exception as e:
            logger.error(e)

    @classmethod
    async def delete_file_from_mongo(cls, request: Request, file_id: str):
        db = request.app.state.mongo_client["files"]
        fs_bucket = AsyncIOMotorGridFSBucket(db)
        fs_bucket.delete(ObjectId(file_id))
        return True


class ExcelRead:
    def __init__(self, df):
        self.df = df

    def find_pars(self):
        # Проверка наличия колонок
        required_columns = ['Дата', 'Работы', 'Примечание']
        for col in required_columns:
            if col not in self.df.columns:
                print(f"Отсутствует обязательная колонка: {col}")
                return None  # Или выбросить исключение

        # Проверка, что есть хотя бы одна строка
        if self.df.empty:
            print("Данных нет.")
            return None
        skv_number = None
        region = None
        mesto_matches = []
        for row in self.df.itertuples():
            # Объединение всех ячеек первой строки в одну строку для поиска
            row_text = ' '.join(str(cell) for cell in row)
            if '> Начало ремонта' in row_text:
                row_begin = row_text.split(';')[0]
                skv_pattern = r'№(\d+)...'

                # Регулярное выражение для даты (день.месяц.год)
                date_pattern = r'(\d{2}\.\d{2}\.\d{4})'

                # Регулярное выражение для времени начала (первое время в диапазоне)
                time_pattern = r'(\d+:\d{2}) - (\d+:\d{2})'

                # Поиск даты
                date_match = re.search(date_pattern, row_begin)
                date_value = date_match.group(1) if date_match else None

                # Поиск времени начала (первое время в диапазоне)
                time_match = re.search(time_pattern, row_begin)
                start_time = time_match.group(1) if time_match else None

                # Поиск номера скважины
                skv_match = re.search(skv_pattern, row_begin)
                skv_number = skv_match.group(1) if skv_match else None
                if ' КР)' in row_begin:
                    region = "КГМ"
                elif ' ТР)' in row_begin:
                    region = "ТГМ"
                elif ' ИР)' in row_begin:
                    region = "ИГМ"
                elif ' АР)' in row_begin:
                    region = "АГМ"
                elif ' ЧР)' in row_begin:
                    region = "ЧГМ"
            mesto_matches = re.findall(r'скв\.?\s*№\s*[\w\-]+(?:\s+)([\w\-]+)', row_text, re.IGNORECASE)
            if ('переезд' in row_text.lower() or 'перестанов' in row_text.lower()) and len(mesto_matches) != 0:
                break

        # if skv_number is None or mesto_matches[0] is None:
        #     return

        return skv_number, mesto_matches, region, date_value + " " + start_time

    @staticmethod
    def extract_datetimes(row):
        # Обработка строки с датой
        date_str = row[1].split('\n')[0]  # '03.08.2025'
        time_range = row[1].split('\n')[1]  # '18:00-22:00'

        # Парсим дату
        date_obj = datetime.strptime(date_str, '%d.%m.%Y')

        # Парсим время начала и конца интервала
        start_time_str, end_time_str = time_range.split('-')
        start_time = datetime.strptime(start_time_str.strip(), '%H:%M').time()
        end_time = datetime.strptime(end_time_str.strip(), '%H:%M').time()


        # Создайте datetime без временной зоны
        start_datetime_naive = datetime.combine(date_obj, start_time)

        # Затем установите временную зону
        start_datetime = start_datetime_naive.replace(tzinfo=ZoneInfo("Asia/Yekaterinburg"))
        end_datetime = datetime.combine(date_obj.date(), end_time)

        return (start_datetime, row[2])

    # Пример использования:
    # df = pd.read_excel('ваш_файл.xls', engine='xlrd')
    # ремонты = проверить_и_найти(df)
    # если нужны только ремонты с этой фразой — они будут в списке ремонты