import io

from fastapi import APIRouter, Form, UploadFile, HTTPException, Depends
from fastapi.params import File
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from fastapi.responses import StreamingResponse
from zimaApp.config import settings
from zimaApp.repairGis.dao import RepairsGisDAO
from zimaApp.repairGis.router import update_repair_gis_data
from zimaApp.repairGis.schemas import RepairGisUpdate
from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users
from bson import ObjectId

router = APIRouter(
    prefix="/files",
    tags=["работа с файлами"],
)

import mimetypes


@router.post("/upload")
async def upload_file(itemId: str = Form(...), file: UploadFile = File(...), user: Users = Depends(get_current_user)):
    client = AsyncIOMotorClient(settings.MONGO_DATABASE_URL)
    db = client['zima_data']
    fs_bucket = AsyncIOMotorGridFSBucket(db)
    # Читаем содержимое файла
    contents = await file.read()
    filename = file.filename

    # Определяем расширение
    ext = '.' + filename.split('.')[-1] if '.' in filename else ''
    # Или определяем MIME тип
    mime_type, _ = mimetypes.guess_type(filename)

    # Сохраняем файл с метаданными о формате
    grid_out_id = await fs_bucket.upload_from_stream(
        filename,
        contents,
        metadata={
            "item_id": itemId,
            "extension": ext,
            "mime_type": mime_type
        }
    )

    file_id = str(grid_out_id)
    file_url = f"/files/{file_id}"

    # Обновление базы данных (пример)
    result_file = RepairGisUpdate(id=int(itemId), fields={"image_pdf": file_url})
    result_file = await update_repair_gis_data(result_file)

    if result_file:
        return {"fileId": file_id, "fileUrl": file_url}


@router.get("/{file_id}")
async def get_file(file_id: str, user: Users = Depends(get_current_user)):
    try:
        client = AsyncIOMotorClient(settings.MONGO_DATABASE_URL)
        db = client['zima_data']
        fs_bucket = AsyncIOMotorGridFSBucket(db)

        grid_out = await fs_bucket.open_download_stream(ObjectId(file_id))

        # Получаем метаданные
        metadata = getattr(grid_out, 'metadata', {}) or {}
        extension = metadata.get('extension')
        mime_type_meta = metadata.get('mime_type')

        # Читаем содержимое файла
        contents = await grid_out.read()

        # Определяем тип контента
        if mime_type_meta:
            content_type = mime_type_meta
        elif extension:
            content_type, _ = mimetypes.guess_type(f"file{extension}")
            if content_type is None:
                content_type = "application/octet-stream"
        else:
            content_type = "application/octet-stream"

        filename_attr = getattr(grid_out, 'filename', None)
        filename_for_header = filename_attr or "file"

        headers = {
            "Content-Disposition": f'inline; filename="{filename_for_header}"'
        }

        return StreamingResponse(io.BytesIO(contents), media_type=content_type, headers=headers)

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Файл не найден: {e}")

@router.delete("/delete")
async def delete_file(data: dict):
    try:
        item_id = data.get("itemId")
        # логика поиска файла по item_id и его удаления
        # например:
        client = AsyncIOMotorClient(settings.MONGO_DATABASE_URL)
        db = client['zima_data']
        fs_bucket = AsyncIOMotorGridFSBucket(db)
        repair_info = await RepairsGisDAO.find_one_or_none(id=int(item_id))
        if repair_info:
            file_id = repair_info["image_pdf"].replace("/files/", "")
            result_file = RepairGisUpdate(id=int(item_id), fields={"image_pdf": None})
            result = await update_repair_gis_data(result_file)
            await fs_bucket.delete(ObjectId(file_id))

            # обновление базы данных
            return {"message": "Файл успешно удален"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}")