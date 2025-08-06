import io
import mimetypes
import urllib

from fastapi import APIRouter, Form, UploadFile, HTTPException, Depends, File, Request

from fastapi.responses import StreamingResponse

from zimaApp.files.dao import MongoFile, ExcelRead
from zimaApp.logger import logger
from zimaApp.repairGis.dao import RepairsGisDAO
from zimaApp.repairGis.router import update_repair_gis_data
from zimaApp.repairGis.schemas import RepairGisUpdate
from zimaApp.tasks.telegram_bot_template import TelegramInfo
from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users

from zimaApp.wells_repair_data.dao import WellsRepairsDAO
from zimaApp.wells_repair_data.models import StatusWorkPlan
from zimaApp.wells_repair_data.router import update_plan_status, find_repair_filter_by_number
from zimaApp.wells_repair_data.schemas import WellsRepairFile

router = APIRouter(
    prefix="/files",
    tags=["работа с файлами"],
)

from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List
import pandas as pd
import io

app = FastAPI()


@router.post("/upload_multiple_excel/")
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
            excel_xlrd = ExcelRead(df)
            excel_result = excel_xlrd.find_pars()

            if excel_result:
                wells_repair = await find_repair_filter_by_number(excel_result[0], user)
                # Обработка данных по необходимости
                data_list = df.to_dict(orient='records')

                results.append({
                    "filename": file.filename,
                    "rows": len(data_list),
                    "data": data_list  # или только часть данных
                })

        except Exception as e:
            return {
                "error": f"Ошибка при обработке файла {file.filename}: {str(e)}"
            }

    return {"files_processed": results}


@router.post("/upload")
async def upload_file_gis_akt(request: Request,
                              itemId: str = Form(...),
                              file: UploadFile = File(...),
                              user: Users = Depends(get_current_user),
                              ):
    file_url, file_id, filename = await MongoFile.upload_file(request, itemId, file)

    result_file = RepairGisUpdate(id=int(itemId), fields={"image_pdf": file_url}, )
    result_file = await update_repair_gis_data(result_file)

    if result_file:
        return {"fileId": file_id, "fileUrl": file_url}


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
                                             status_work_plan=StatusWorkPlan.NOT_SIGNED)
                result = await update_plan_status(new_status)

                # обновление базы данных
                return {"message": "Файл успешно удален"}


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
