from dns.asyncquery import https
from fastapi import APIRouter, Depends, HTTPException
from datetime import date, timedelta, datetime, timezone

from sqlalchemy.exc import SQLAlchemyError

from zimaApp.config import settings
from zimaApp.exceptions import DowntimeDurationAlreadyExistsException
from zimaApp.logger import logger
from zimaApp.repairGis.dao import RepairsGisDAO
from zimaApp.repairGis.models import RepairsGis
from zimaApp.repairGis.schemas import (
    SRepairsGis,
    RepairGisUpdate,
    RepairGisResponse,
    ColumnEnum,
)
from zimaApp.tasks.telegram_bot_template import TelegramInfo

from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users
from zimaApp.well_silencing.router import WellsSearchArgs
from zimaApp.wells_data.dao import WellsDatasDAO
from zimaApp.wells_data.router import find_wells_data
from zimaApp.wells_data.schemas import SWellsData
from zimaApp.brigade.dao import BrigadeDAO
from zimaApp.brigade.schemas import SWellsBrigade, SBrigadeSearch
from fastapi_versioning import version

router = APIRouter(
    prefix="/repair_gis",
    tags=["Данные по простоям ГИС"],
)


@router.get("")
@version(1)
async def repairs_gis():
    return {"status": "ok", "data": "пример данных"}


@router.get("/all")
@version(1)
async def get_repair_gis_all():
    try:
        repairs = await RepairsGisDAO.filter_for_filter(
            model=RepairsGis, join_related="well"
        )
        # Формируем список ответов, извлекая нужные поля
        response_list = []
        for repair in repairs:
            response_list.append(
                RepairGisResponse(
                    id=repair.id,
                    well_number=repair.well.well_number,  # предполагается, что есть поле number в WellsData
                    well_area=repair.well.well_area,  # предполагается, что есть поле area в WellsData
                    status=repair.status,
                    contractor_gis=repair.contractor_gis,
                    message_time=repair.message_time,
                    downtime_start=repair.downtime_start,
                    downtime_end=repair.downtime_end,
                    downtime_duration=repair.downtime_duration,
                    downtime_reason=repair.downtime_reason,
                    work_goal=repair.work_goal,
                    contractor_opinion=repair.contractor_opinion,
                    downtime_duration_meeting_result=repair.downtime_duration_meeting_result,
                    meeting_result=repair.meeting_result,
                    image_pdf=repair.image_pdf,
                )
            )
        if len(response_list) != 0:
            response_list = sorted(
                [resp.model_dump() for resp in response_list],
                key=lambda x: x["downtime_start"],
                reverse=True,
            )

        return response_list

    except SQLAlchemyError as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)


@router.get("/get_find_data_column")
@version(1)
async def get_find_data_column(
    column_name: ColumnEnum, user: Users = Depends(get_current_user)
):
    try:
        records = await RepairsGisDAO.filter_for_filter(
            model=RepairsGis, join_related="well"
        )

        result_list = {}

        for record in records:
            if column_name == "well_number":
                result_list.setdefault("well_number", []).append(
                    record.well.well_number
                )
            elif column_name == "well_area":
                result_list.setdefault("well_area", []).append(record.well.well_area)
            elif column_name == "downtime_start":
                result_list.setdefault("downtime_start", []).append(
                    record.downtime_start
                )
            else:
                result_list.setdefault(column_name, []).append(
                    record.__dict__[column_name]
                )

        return result_list

    except SQLAlchemyError as e:
        logger.error(e)
        return {"error": str(e)}
    except Exception as e:
        logger.error(e)
        return {"error": str(e)}


@router.get("/get_data_by_filter_column")
@version(1)
async def get_data_by_filter_column(
    column_name: ColumnEnum, filter_value: str, user: Users = Depends(get_current_user)
):
    # Маппинг колонок на поля модели
    valid_columns = {
        "id": RepairsGis.id,
        "well_number": RepairsGis.well.well_number,
        "well_area": RepairsGis.well.well_area,
        "status": RepairsGis.status,
        "contractor_gis": RepairsGis.contractor_gis,
        "downtime_start": RepairsGis.downtime_start,
        # добавьте остальные поля по необходимости
    }

    # if column_name.value not in valid_columns:
    #     raise HTTPException(status_code=400, detail="Invalid column name")
    #
    # filter_field = valid_columns[column_name.value]

    # Формируем фильтр
    filter_by = {column_name.name: filter_value}

    repairs = await RepairsGisDAO.filter_for_filter(
        model=RepairsGis, filter_by=filter_by, join_related="well"
    )

    return repairs


@router.post("/add_data")
@version(1)
async def add_wells_data(repair_info: SRepairsGis):
    from zimaApp.main import bot_user

    try:
        if repair_info:
            result = await RepairsGisDAO.find_one_or_none(downtime_start=repair_info.downtime_start)
            if result is None:
                # await delete_brigade(repair_info)
                result = await RepairsGisDAO.add_data(
                    status="открыт",
                    well_id=repair_info.well_id,
                    contractor_gis=repair_info.contractor_gis,
                    message_time=repair_info.message_time,
                    downtime_start=repair_info.downtime_start,
                    downtime_end=repair_info.downtime_end,
                    downtime_duration=repair_info.downtime_duration,
                    downtime_reason=repair_info.downtime_reason,
                    work_goal=repair_info.work_goal,
                    contractor_opinion=repair_info.contractor_opinion,
                    downtime_duration_meeting_result=repair_info.downtime_duration_meeting_result,
                    meeting_result=repair_info.meeting_result,
                    image_pdf=None,
                )

                await bot_user.send_message(chat_id=settings.CHAT_ID, text=result)

            return {"status": "success", "id": result}

    except SQLAlchemyError as db_err:
        msg = f"Database Exception Brigade {db_err}"
        logger.error(
            msg,
            extra={"number_brigade": repair_info.well_id.well_number},
            exc_info=True,
        )

    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(
            msg,
            extra={"number_brigade": repair_info.well_id.well_number},
            exc_info=True,
        )


@router.put("/update")
async def update_repair_gis_data(
    repair_info: RepairGisUpdate, user: Users = Depends(get_current_user)
):
    try:
        repair_dict = repair_info.model_dump()
        if repair_info:
            if "downtime_end" in repair_info.fields:
                result = await RepairsGisDAO.find_one_or_none(id=repair_info.id)
                time_finish = datetime.fromisoformat(
                    repair_info.fields["downtime_end"]
                ).astimezone(timezone.utc) + timedelta(hours=5)
                time_run = result.downtime_start
                downtime_duration = time_finish - time_run

                # Проверяем, что длительность положительна
                if downtime_duration <= timedelta(0):
                    raise DowntimeDurationAlreadyExistsException
                    return

                repair_dict["fields"]["downtime_duration"] = float(
                    downtime_duration.total_seconds() / 3600
                )
                repair_dict["fields"]["downtime_end"] = time_finish

            result = await RepairsGisDAO.update(
                {"id": repair_info.id}, **repair_dict["fields"]
            )

            # await TelegramInfo.send_message_update_brigade(user.login_user, repair_info.number_brigade,
            #                                                brigade.contractor)

            return result
    except SQLAlchemyError as db_err:
        msg = f"Database Exception Brigade {db_err}"
        logger.error(
            msg,
            extra={
                "number_brigade": repair_info.number_brigade,
                "contractor": repair_info.contractor,
            },
            exc_info=True,
        )
        return {"error": str(msg)}

    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(
            msg,
            extra={
                "number_brigade": repair_info.number_brigade,
                "contractor": repair_info.contractor,
            },
            exc_info=True,
        )
        return {"error": str(e)}


@router.delete("/delete_brigade")
@version(1)
async def delete_brigade(
    brigade: SWellsBrigade = Depends(), user: Users = Depends(get_current_user)
):
    data = await RepairsGisDAO.find_one_or_none(brigade)
    if data:
        return await BrigadeDAO.delete_item_all_by_filter(
            number_brigade=brigade.number_brigade, contractor=brigade.contractor
        )
