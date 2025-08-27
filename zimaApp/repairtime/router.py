from datetime import datetime, timedelta, timezone
from typing import List
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends

from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from zimaApp.brigade.models import Brigade
from zimaApp.brigade.router import find_brigade_by_id
from zimaApp.exceptions import ExceptionError, WellsAlreadyExistsException, BrigadeAlreadyExistsException, \
    WellsClosedExistsException
from zimaApp.logger import logger
from zimaApp.prometheus.router import time_consumer
from zimaApp.repairtime.dao import RepairTimeDAO
from zimaApp.repairtime.models import StatusSummary, RepairTime
from zimaApp.repairtime.schemas import SRepairTime, SRepairTimeClose, SRepairNorm
from zimaApp.summary.schemas import SUpdateSummary

from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users
from fastapi_versioning import version

from zimaApp.wells_data.models import WellsData
from zimaApp.wells_data.router import find_wells_data_by_id
from zimaApp.wells_repair_data.models import StatusWorkPlan, WellsRepair
from zimaApp.wells_repair_data.router import find_repair_id

router = APIRouter(
    prefix="/repair_time",
    tags=["Сводная времени сводки"],
)


@router.get("/check_well_id_and_end_time")
@version(1)
async def check_well_id_and_end_time(well_id: int, open_datetime: datetime, user: Users = Depends(get_current_user)):
    try:
        result = await RepairTimeDAO.find_one_or_none(well_id=well_id, end_time=None)
        if result:
            if open_datetime > result.start_time:
                return result
    except SQLAlchemyError as db_err:
        msg = f"Database Exception Brigade {db_err}"
        logger.error(msg, exc_info=True)
    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg, exc_info=True)
        raise ExceptionError(msg)

@router.get("/get_type_kr_by_id")
@version(1)
async def get_type_kr_by_id(repair_id: int, user: Users=Depends(get_current_user)):
    result = await RepairTimeDAO.get_type_kr(repair_time_id=repair_id)
    return result

@router.get("/check_brigade_id_and_end_time")
@version(1)
async def check_brigade_id_and_end_time(brigade_id: int, open_datetime: datetime,
                                        user: Users = Depends(get_current_user)):
    try:
        result = await RepairTimeDAO.find_one_or_none(brigade_id=brigade_id, end_time=None)
        if result:
            if open_datetime > result.start_time:
                return result

    except SQLAlchemyError as db_err:
        msg = f"Database Exception Brigade {db_err}"
        logger.error(msg, exc_info=True)
    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg, exc_info=True)
        raise ExceptionError(msg)


@router.get("/find_by_id_repair")
@version(1)
async def find_by_id_repair(summary_id: int, user: Users = Depends(get_current_user)):
    try:
        result = await RepairTimeDAO.find_by_id_repair(summary_id)
        if result:
            return result
    except SQLAlchemyError as db_err:
        msg = f"Database Exception Summary {db_err}"
        logger.error(msg, extra={"summary": summary_id})
        raise ExceptionError(msg)

    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg, extra={"summary": summary_id})
        raise ExceptionError(msg)


@router.get("/find_repair_params_by_id")
@version(1)
async def find_repair_params_by_id(repair_id: int, user: Users = Depends(get_current_user)):
    try:
        result = await RepairTimeDAO.find_repair_params_by_id(repair_id=repair_id)
        if result:
            return result
    except SQLAlchemyError as db_err:
        msg = f"Database Exception Summary {db_err}"
        logger.error(msg, extra={"id": repair_id})
        raise ExceptionError(msg)

    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg, extra={"id": repair_id})
        raise ExceptionError(msg)


@router.post("/add")
@version(1)
async def open_summary_data(
        open_datetime: datetime,
        summary_info: SUpdateSummary,
        wells_repair: WellsRepair = Depends(),
        well_data: WellsData = Depends(find_wells_data_by_id),
        brigade: Brigade = Depends(find_brigade_by_id),

        user: Users = Depends(get_current_user)
):
    open_datetime = open_datetime  # + timedelta(hours=5)

    check_wells = await check_well_id_and_end_time(well_data.id, open_datetime)
    if check_wells:
        return WellsAlreadyExistsException

    check_brigade = await check_brigade_id_and_end_time(brigade.id, open_datetime)
    if check_brigade:
        return BrigadeAlreadyExistsException

    try:
        if summary_info:
            result_date, result_time, result_interval = await RepairTimeDAO.get_date_and_interval(
                summary_info.date_summary)
            check_start_wells = await RepairTimeDAO.find_one_or_none(well_id=well_data.id, status="закрыт",
                                                                     start_time=open_datetime)
            if check_start_wells:
                mes = f"Скважина {well_data.well_number} c началом ремонта уже загружена и закрыта"
                logger.info(mes)
                return WellsClosedExistsException

            summary_data = {
                "date_summary": result_date,
                "time_interval": result_interval,
                "notes": None,
                "act_path": None,
                "status_act": StatusWorkPlan.NOT_SIGNED.value,
                "photo_path": None,
                "video_path": None
            }
            if not wells_repair is None:
                wells_repair = wells_repair.id

            repair_data = {
                'well_id': well_data.id,
                'start_time': open_datetime,
                'end_time': None,
                "brigade_id": brigade.id,
                "wells_repair_id": wells_repair

            }

            result = await RepairTimeDAO.add_brigade_with_repairs(summary_data, repair_data)
            if result:
                return {"status_code": status.HTTP_200_OK, "success": "OK", "data": result}

    except SQLAlchemyError as db_err:
        msg = f"Database Exception Brigade {db_err}"
        logger.error(
            msg,
            # extra={
            #     "number_brigade": brigade_info.number_brigade,
            #     "contractor": brigade_info.contractor,
            # },
            exc_info=True,
        )
        raise ExceptionError(msg)

    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(
            msg,
            # extra={
            #     "number_brigade": brigade_info.number_brigade,
            #     "contractor": brigade_info.contractor,
            # },
            exc_info=True,
        )
        raise ExceptionError(msg)


@router.get("/get_repair_time_by_well_number")
@version(1)
async def get_repair_time_by_well_number(
        well_number: str,
        user: Users = Depends(get_current_user)) -> List:
    try:
        repairs = await RepairTimeDAO.find_by_well_number(well_number=well_number)
        new_repair = []
        for row in repairs:
            new_repair.append(
                f"{row.well.well_number} {row.well.well_area} от {row.start_time.strftime('%d.%m.%Y')} "
                f"Бр№{row.brigade.number_brigade} id№{row.id} "
            )
        return new_repair

    except SQLAlchemyError as db_err:
        msg = f"Database Exception filter {db_err}"
        logger.error(msg)
    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg, exc_info=True)
        raise ExceptionError(msg)


@router.get("/find_all_by_filter_status")
@version(1)
async def find_all_by_filter_status(status=None,
                                    user: Users = Depends(get_current_user)):
    try:
        repairs = await RepairTimeDAO.get_all(status=status)
        serialized_data = []
        for repair in repairs:
            data = {"id": repair.id,
                    "Номер Бригады": f"Бр №{repair.brigade.number_brigade}",
                    "Номер скважины": repair.well.well_number,
                    "площадь": repair.well.well_area,
                    "Месторождение": repair.well.well_oilfield,
                    "Статус ремонта": repair.status,
                    "Дата открытия ремонта": repair.start_time.astimezone(ZoneInfo("Asia/Yekaterinburg")).strftime(
                        "%Y-%m-%d %H:%M"),
                    "Дата закрытия ремонта": repair.end_time.astimezone(ZoneInfo("Asia/Yekaterinburg")).strftime(
                        "%Y-%m-%d %H:%M") if repair.end_time else repair.end_time,
                    # "Продолжительность ремонта": timedelta(datetime.now().timetz() - repair.start_time).hours()
                    "Продолжительность ремонта": None
                    }

            serialized_data.append(data)

        if serialized_data:
            return serialized_data
    except SQLAlchemyError as db_err:
        msg = f"Database Exception filter {db_err}"
        logger.error(msg)
        raise ExceptionError(msg)
    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg, exc_info=True)
        raise ExceptionError(msg)


@router.get("/find_all")
@version(1)
async def find_all(user: Users = Depends(get_current_user)):
    try:
        repair = await RepairTimeDAO.find_all()
        if repair:
            return {"status": "success", "data": repair}
    except SQLAlchemyError as db_err:
        msg = f"Database Exception filter {db_err}"
        logger.error(msg)
        raise ExceptionError(msg)
    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg, exc_info=True)
        raise ExceptionError(msg)


@router.get("/find_one_repair")
@version(1)
async def find_one_repair(repair_id: int, user: Users = Depends(get_current_user)):
    try:
        repair_info = await RepairTimeDAO.find_one_or_none(id=repair_id)
        if repair_info:
            return
    except SQLAlchemyError as db_err:
        msg = f"Database Exception RepairTima {db_err}"
        logger.error(msg, extra={" repair_id": repair_id})
        raise ExceptionError(msg)
    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg, extra={" repair_id": repair_id})
        raise ExceptionError(msg)


@router.put("/update_repair_time")
@version(1)
async def update_repair_time(
        repair_info: SRepairTimeClose = Depends(),
        repair: SRepairTime = Depends(find_one_repair),
        user: Users = Depends(get_current_user)
):
    try:
        result = await RepairTimeDAO.update_data(
            id=repair_info.id,
            end_time=repair.end_time)
        if result:
            return {"status": "success", "id": result}
    except SQLAlchemyError as db_err:
        msg = f"Database Exception RepairTima {db_err}"
        logger.error(msg, extra={" repair_id": repair_info.id})
        raise ExceptionError(msg)
    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg, extra={" repair_id": repair_info.id})
        raise ExceptionError(msg)

@router.put("/update_repair_time_json")
@version(1)
async def update_repair_norms_json(
        repair_info: SRepairNorm = Depends(),
        user: Users = Depends(get_current_user)
):
    try:
        result = await RepairTimeDAO.update_data(
            id=repair_info.id,
            norms_work=repair_info.norms_work,
            norms_time=repair_info.norms_time)

        if result:
            return {"status": "success", "id": result}
    except SQLAlchemyError as db_err:
        msg = f"Database Exception RepairTima {db_err}"
        logger.error(msg, extra={" repair_id": repair_info.id})
        raise ExceptionError(msg)
    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg, extra={" repair_id": repair_info.id})
        raise ExceptionError(msg)


@router.delete("/delete")
@version(1)
async def delete_brigade(
        repair: SRepairTime = Depends(find_one_repair),
        user: Users = Depends(get_current_user)
):
    try:

        return await RepairTimeDAO.delete_item_all_by_filter(
            id=repair.brigade_summary_id
        )
    except SQLAlchemyError as db_err:
        msg = f"Database Exception RepairTima {db_err}"
        logger.error(msg, extra={" repair_id": repair.id})
        raise ExceptionError(msg)
    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg, extra={" repair_id": repair.id})
        raise ExceptionError(msg)
