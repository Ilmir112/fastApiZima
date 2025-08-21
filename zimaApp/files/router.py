
import mimetypes
import re
import urllib
from datetime import time, datetime, timedelta
from enum import Enum

from fastapi import APIRouter, Form, Depends,  Request
from fastapi_versioning import version

from fastapi.responses import StreamingResponse

from zimaApp.brigade.router import find_brigade_by_number
from zimaApp.files.dao import MongoFile, ExcelRead
from zimaApp.logger import logger

from zimaApp.repairGis.dao import RepairsGisDAO
from zimaApp.repairGis.router import update_repair_gis_data
from zimaApp.repairGis.schemas import RepairGisUpdate
from zimaApp.repairtime.dao import RepairTimeDAO
from zimaApp.repairtime.router import open_summary_data
from zimaApp.summary.dao import BrigadeSummaryDAO
from zimaApp.summary.router import update_repair_summary, add_summary
from zimaApp.summary.schemas import DeletePhotoRequest, SUpdateSummary
from zimaApp.tasks.tasks import work_with_excel_summary
from zimaApp.tasks.telegram_bot_template import TelegramInfo
from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users
from zimaApp.wells_data.dao import WellsDatasDAO

from zimaApp.wells_repair_data.dao import WellsRepairsDAO
from zimaApp.wells_repair_data.models import StatusWorkPlan
from zimaApp.wells_repair_data.router import update_plan_status
from zimaApp.wells_repair_data.schemas import WellsRepairFile
from fastapi import File, UploadFile, HTTPException
from typing import List
import pandas as pd
import io

router = APIRouter(
    prefix="/files",
    tags=["работа с файлами"],
)


class PathEnum(str, Enum):
    ACT_PATH = "act_path"
    VIDEO_PATH = "video_path"
    PHOTO_PATH = "photo_path"


@router.post("/upload_images")
async def upload_images(
        request: Request,
        itemId: str,  # Предполагается, что itemId передается как параметр или из тела запроса
        files: List[UploadFile] = File(...),
        user: Users = Depends(get_current_user)):
    results = []

    for file in files:
        try:
            # Загружаем файл через ваш метод MongoFile.upload_file
            file_url, file_id, filename = await MongoFile.upload_file(request, itemId, file)

            # После успешной загрузки можно сохранить информацию в базе данных или выполнить другие действия
            # Например, добавление записи о файле в коллекцию

            results.append((file_url, filename))

        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e),
                "status": "failed"
            })
    result = await BrigadeSummaryDAO.update_data(int(itemId), photo_path=results)
    return results


@router.post("/upload_multiple_excel")
async def upload_multiple_excel(
        files: List[UploadFile] = File(...),
        user: Users = Depends(get_current_user)):
    results = []

    for file in files:
        # Проверка типа файла
        if not file.filename.endswith(('.xlsx', '.xls')):
            return {
                "error": f"Некорректный тип файла: {file.filename}. Загрузите Excel файл."
            }

        try:
            contents = await file.read()
            excel_data = io.BytesIO(contents)
            df = pd.read_excel(excel_data)
            filename = file.filename

            results = await work_with_excel_summary(filename, df, user)

        except Exception as e:
            return {
                "error": f"Ошибка при обработке файла {filename}: {str(e)}"
            }

    return {"files_processed": results}


@router.get("/open_files_video")
@version(1)
async def get_open_files(request: Request, files_id: int, status_file: PathEnum) -> List:
    try:
        result = await BrigadeSummaryDAO.find_one_or_none(id=files_id)

        if result:

            adasf = result[f'{status_file.value}']
            return [result[f'{status_file.value}']] \
                if status_file.value != 'photo_path' else result[f'{status_file.value}']
    except Exception as e:
        print(str(e))


@router.post("/upload")
async def upload_file_gis_akt(request: Request,
                              itemId: str = Form(...),
                              file: UploadFile = File(...),
                              user: Users = Depends(get_current_user),
                              ):
    file_url, file_id, filename = await MongoFile.upload_file(request, itemId, file)

    result_file = RepairGisUpdate(id=int(itemId), fields={"image_pdf": (file_url, filename)}, )
    result_file = await update_repair_gis_data(result_file)

    if result_file:
        return {"fileId": file_id, "fileUrl": file_url}


@router.post("/upload_video")
async def upload_file_gis_akt(request: Request,
                              itemId: str = Form(...),
                              file: UploadFile = File(...),
                              user: Users = Depends(get_current_user),
                              ):
    if file.size > 12000007:
        return {"status": "Слишком большой объем видео"}
    file_url, file_id, filename = await MongoFile.upload_file(request, itemId, file)

    update_file = RepairGisUpdate(id=int(itemId),
                                  fields={"video_path": [file_url, filename]})

    result_file = await update_repair_summary(update_file)

    if result_file:
        return {"fileId": file_id, "fileUrl": file_url}


@router.post("/upload_summary_act")
async def upload_file_summary(request: Request,
                              itemId: str = Form(...),
                              file: UploadFile = File(...),
                              status: str = Form(...),
                              user: Users = Depends(get_current_user),
                              ):
    try:
        file_url, file_id, filename = await MongoFile.upload_file(request, itemId, file)

        # update_file = RepairGisUpdate(id=int(itemId),
        #                               fields={"act_path": file_url, "status_act": status})

        result_file = await BrigadeSummaryDAO.update(filter_by={"id": int(itemId)}, act_path=(file_url, filename), status_act=status)

        if result_file:
            return {"fileId": file_id, "fileUrl": file_url}
    except Exception as e:
        logger.error(str(e))


@router.get("/{file_id}")
async def get_file(request: Request, file_id: str, user: Users = Depends(get_current_user)):
    try:
        grid_out = await MongoFile.get_file_from_mongo(request, file_id)
        if grid_out:
            # Получаем метаданные
            metadata = getattr(grid_out, "metadata", {}) or {}
            extension = metadata.get("extension")
            mime_type_meta = metadata.get("mime_type")

            # Читаем содержимое файла
            contents = await grid_out.read()

            # Определяем тип контента
            if mime_type_meta:
                content_type = mime_type_meta
            elif extension:
                guessed_type, _ = mimetypes.guess_type(f"file{extension}")
                content_type = guessed_type or "application/octet-stream"
            else:
                content_type = metadata.get('contentType')

            filename_attr = getattr(grid_out, "filename", None)
            filename_for_header = filename_attr or "file"
            filename_encoded = urllib.parse.quote(filename_for_header)

            return StreamingResponse(
                io.BytesIO(contents),
                media_type=content_type,
                headers={
                    "Content-Disposition": f"inline; filename*=UTF-8''{filename_encoded}"
                }
            )
        else:
            return {"error": "File not found"}
    except Exception as e:
        # Логирование или обработка ошибок
        return {"error": str(e)}


@router.delete("/delete_plan")
async def delete_file(request: Request,
                      data: dict):
    item_id = data.get("itemId")
    plan_info = await WellsRepairsDAO.find_one_or_none(id=int(item_id))
    if plan_info:
        file_id = plan_info["signed_work_plan_path"]
        if file_id:

            result_mongo = await MongoFile.delete_file_from_mongo(request, file_id.replace("/files/", ""))
            if result_mongo:
                new_status = WellsRepairFile(id=int(item_id),
                                             signed_work_plan_path=None,
                                             status_work_plan=StatusWorkPlan.NOT_SIGNED.value)
                result = await update_plan_status(new_status)

                # обновление базы данных
                return {"message": "Файл успешно удален"}


@router.delete("/delete_video")
async def delete_video(request: Request,
                       data: dict):
    item_id = data.get("itemId")
    plan_info = await BrigadeSummaryDAO.find_one_or_none(id=int(item_id))
    if plan_info:
        file_id = [plan_info["video_path"]]
        if file_id:
            for file_path, _ in file_id:
                result_mongo = await MongoFile.delete_file_from_mongo(request, file_path.replace("/files/", ""))
            if result_mongo:
                result = await BrigadeSummaryDAO.update_data(int(item_id), video_path=None)
                # обновление базы данных
                return {"message": "Файл успешно удален"}
    return {"message": "Файл отсутствует"}


@router.delete("/delete_photo")
async def delete_photo(request: Request, data: DeletePhotoRequest):
    try:
        item_id = data.itemId
        # Находим запись по itemId
        summary_info = await BrigadeSummaryDAO.find_one_or_none(id=item_id)
        if not summary_info:
            raise HTTPException(status_code=404, detail="Запись не найдена")

        files_path = summary_info.get("photo_path")
        if not files_path:
            return {"success": False, "message": "Файл не найден или уже удален"}

        for file_path, _ in files_path:
            result_mongo = await MongoFile.delete_file_from_mongo(request, file_path.replace("/files/", ""))
            if not result_mongo:
                raise HTTPException(status_code=500, detail="Ошибка при удалении файла из хранилища")

        if result_mongo:
            result = await BrigadeSummaryDAO.update_data(int(item_id), photo_path=None)


        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.delete("/delete_act")
async def delete_act(request: Request,
                     data: dict):
    try:
        item_id = data.get("itemId")
        summary_info = await BrigadeSummaryDAO.find_one_or_none(id=int(item_id))
        if summary_info:
            file_id = summary_info["act_path"]
            if file_id:
                result_mongo = await MongoFile.delete_file_from_mongo(request, file_id[0].replace("/files/", ""))
                if result_mongo:
                    result = await BrigadeSummaryDAO.update_data(int(item_id), act_path=None,
                                                                 status_act=StatusWorkPlan.NOT_SIGNED.value)

                # обновление базы данных
                return {"message": "Файл успешно удален"}
    except Exception as e:
        return {"error": str(e)}


@router.delete("/delete_act_gis")
async def delete_file(request: Request, data: dict):
    try:
        item_id = data.get("itemId")
        repair_info = await RepairsGisDAO.find_one_or_none(id=int(item_id))
        if repair_info:

            file_id = repair_info["image_pdf"]
            if file_id:
                result_file = RepairGisUpdate(id=int(item_id), fields={"image_pdf": None})
                result_mongo = await MongoFile.delete_file_from_mongo(request, file_id.replace("/files/", ""))
                if result_mongo:
                    result = await update_repair_gis_data(result_file)

                    # обновление базы данных
                    return {"message": "Файл успешно удален"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}")


@router.post("/upload_plan")
async def upload_plan(request: Request,
                      itemId: str = Form(...),
                      file: UploadFile = File(...),
                      status: str = Form(...),
                      user: Users = Depends(get_current_user),
                      ):
    try:
        file_url, file_id, filename = await MongoFile.upload_file(request, itemId, file)
        result_file = WellsRepairFile(id=int(itemId),
                                      signed_work_plan_path=file_url,
                                      status_work_plan=status)
        if result_file:
            result = await update_plan_status(result_file)
            if result:
                await TelegramInfo.send_message_add_plan_pdf(
                    user.login_user, result_file.id, result_file.status_work_plan
                )
            return {"fileId": file_id, "fileUrl": file_url}
    except Exception as e:
        logger.error(e)
