import io
import mimetypes

from fastapi import APIRouter, Form, UploadFile, HTTPException, Depends, File

from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

from zimaApp.files.dao import MongoFile

from zimaApp.repairGis.dao import RepairsGisDAO
from zimaApp.repairGis.router import update_repair_gis_data
from zimaApp.repairGis.schemas import RepairGisUpdate
from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users

from zimaApp.wells_repair_data.dao import WellsRepairsDAO
from zimaApp.wells_repair_data.models import StatusWorkPlan
from zimaApp.wells_repair_data.router import update_plan_status
from zimaApp.wells_repair_data.schemas import WellsRepairFile

router = APIRouter(
    prefix="/files",
    tags=["работа с файлами"],
)


def get_fs_bucket() -> AsyncIOMotorGridFSBucket:
    from zimaApp.main import fs_bucket
    return fs_bucket

@router.post("/upload")
async def upload_file_gis_akt(
        itemId: str = Form(...),
        file: UploadFile = File(...),
        fs: AsyncIOMotorGridFSBucket = Depends(get_fs_bucket),
        user: Users = Depends(get_current_user),
):

    file_url, file_id, filename = await MongoFile.upload_file(itemId, file, fs)

    result_file = RepairGisUpdate(id=int(itemId), fields={"image_pdf": file_url}, )
    result_file = await update_repair_gis_data(result_file)

    if result_file:
        return {"fileId": file_id, "fileUrl": file_url}


@router.get("/{file_id}")
async def get_file(file_id: str,
                   fs: AsyncIOMotorGridFSBucket = Depends(get_fs_bucket),
                   user: Users = Depends(get_current_user)):
    try:

        grid_out = await MongoFile.get_file_from_mongo(file_id, fs)
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
                content_type, _ = mimetypes.guess_type(f"file{extension}")
                if content_type is None:
                    content_type = "application/octet-stream"
            else:
                content_type = "application/octet-stream"

            filename_attr = getattr(grid_out, "filename", None)
            filename_for_header = filename_attr or "file"

            headers = {"Content-Disposition": f'inline; filename="{filename_for_header}"'}

            return StreamingResponse(
                io.BytesIO(contents), media_type=content_type, headers=headers
            )

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Файл не найден: {e}")


@router.delete("/delete_plan")
async def delete_file(data: dict,
                      fs: AsyncIOMotorGridFSBucket = Depends(get_fs_bucket),
                      user: Users = Depends(get_current_user)):


    item_id = data.get("itemId")
    plan_info = await WellsRepairsDAO.find_one_or_none(id=int(item_id))
    if plan_info:
        file_id = plan_info["signed_work_plan_path"]
        if file_id:

            result_mongo = await MongoFile.delete_file_from_mongo(file_id.replace("/files/", ""), fs)
            if result_mongo:
                new_status = WellsRepairFile(id=int(item_id),
                                             signed_work_plan_path=None,
                                             status_work_plan=StatusWorkPlan.NOT_SIGNED)
                result = await update_plan_status(new_status)

                # обновление базы данных
                return {"message": "Файл успешно удален"}


@router.delete("/delete_act_gis")
async def delete_file(data: dict,
                      fs: AsyncIOMotorGridFSBucket = Depends(get_fs_bucket),
                      user: Users = Depends(get_current_user)):


    try:
        item_id = data.get("itemId")
        repair_info = await RepairsGisDAO.find_one_or_none(id=int(item_id))
        if repair_info:

            file_id = repair_info["image_pdf"]
            if file_id:
                result_file = RepairGisUpdate(id=int(item_id), fields={"image_pdf": None})
                result_mongo = await MongoFile.delete_file_from_mongo(file_id.replace("/files/", ""), fs)
                if result_mongo:
                    result = await update_repair_gis_data(result_file)

                    # обновление базы данных
                    return {"message": "Файл успешно удален"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}")


@router.post("/upload_plan")
async def upload_plan(
        itemId: str = Form(...),
        file: UploadFile = File(...),
        status: str = Form(...),
        user: Users = Depends(get_current_user),
):


    try:
        file_url, file_id, filename = await MongoFile.upload_file(itemId, file)
        result_file = WellsRepairFile(id=int(itemId),
                                      signed_work_plan_path=file_url,
                                      status_work_plan=status)
        if result_file:
            result = await update_plan_status(result_file)
            return {"fileId": file_id, "fileUrl": file_url}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}")
