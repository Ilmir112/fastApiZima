from datetime import datetime, timedelta, timezone
from typing import List
from zoneinfo import ZoneInfo

from celery.bin.result import result
from fastapi import APIRouter, Depends

from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from zimaApp.brigade.models import Brigade
from zimaApp.brigade.router import find_brigade_by_id
from zimaApp.exceptions import ExceptionError, WellsAlreadyExistsException, BrigadeAlreadyExistsException, \
    WellsClosedExistsException
from zimaApp.logger import logger
from zimaApp.prometheus.router import time_consumer
from zimaApp.repair_data.dao import RepairDataDAO
from zimaApp.repair_data.models import RepairData
from zimaApp.repair_data.schemas import RepairDataCreate, SRepairGet
from zimaApp.repairtime.dao import RepairTimeDAO
from zimaApp.repairtime.models import StatusSummary, RepairTime
from zimaApp.repairtime.schemas import SRepairTime, SRepairTimeClose
from zimaApp.summary.schemas import SUpdateSummary

from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users
from fastapi_versioning import version

from zimaApp.wells_data.models import WellsData
from zimaApp.wells_data.router import find_wells_data_by_id
from zimaApp.wells_repair_data.models import StatusWorkPlan, WellsRepair
from zimaApp.wells_repair_data.router import find_repair_id

router = APIRouter(
    prefix="/repairs_data",
    tags=["Перечень ремонта от заказчика"],
)

@router.post("/add")
@version(1)
async def add_repair_data(repair_data: RepairDataCreate, user: Users =Depends(get_current_user)):
    try:
        result_find = await RepairDataDAO.find_one_or_none(brigade_number=repair_data.brigade_number,
            well_area=repair_data.well_area,
            well_number=repair_data.well_number,
            begin_time=repair_data.begin_time)
        if result_find:
            result = await RepairDataDAO.update_data(
                result_find.id,
                finish_time=repair_data.finish_time.replace(tzinfo=ZoneInfo("Asia/Yekaterinburg")) if repair_data.finish_time else None)
        else:
            result = await RepairDataDAO.add_data(
                contractor=repair_data.contractor,
                brigade_number=repair_data.brigade_number,
                well_area=repair_data.well_area,
                well_number=repair_data.well_number,
                begin_time=repair_data.begin_time.replace(tzinfo=ZoneInfo("Asia/Yekaterinburg")),
                finish_time=repair_data.finish_time.replace(tzinfo=ZoneInfo("Asia/Yekaterinburg")) if repair_data.finish_time else None,
                duration_repair=repair_data.duration_repair,
                category_repair=repair_data.category_repair,
                repair_code=repair_data.repair_code,
                type_repair=repair_data.type_repair,
                bush=repair_data.bush
                )
            msg = f"wells indo added in Database"
            logger.info(msg, extra={"well_number": repair_data.well_number})
        return result
    except SQLAlchemyError as db_err:
        msg = f"Database Exception Summary {db_err}"
        logger.error(msg, extra={"repair_data": repair_data})
        raise ExceptionError(msg)

    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg, extra={"repair_data": repair_data})
        raise ExceptionError(msg)

@router.get("/find_all")
@version(1)
async def find_repair_all(user: Users = Depends(get_current_user)):
    try:

        repair = await RepairDataDAO.find_all()
        if repair:
            serialized_data = []
            for data in sorted(repair, key=lambda x: x.begin_time, reverse=True):
                serialized_data.append(
                    {   "id": data.id,
                        "contractor": data.contractor,
                        "brigade_number": data.brigade_number,
                        "well_area": data.well_area,
                        "well_number": data.well_number,
                        "begin_time": data.begin_time.astimezone(ZoneInfo("Asia/Yekaterinburg")).strftime(
                        "%Y-%m-%d %H:%M"),
                        "finish_time": data.finish_time.astimezone(ZoneInfo("Asia/Yekaterinburg")).strftime(
                        "%Y-%m-%d %H:%M") if data.finish_time else None,
                        "category_repair": data.category_repair,
                        "duration_repair": data.duration_repair,
                        "repair_code": data.repair_code,
                        "type_repair": data.type_repair,
                        "bush": data.bush,
                    })
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


@router.get("/get_by_well_number_and_well_area_and_start_repair")
@version(1)
async def get_by_well_number_and_well_area_and_start_repair(
        repair: SRepairGet=Depends(),
        user: Users = Depends(get_current_user)):
    try:
        repair_info = await RepairDataDAO.find_one_or_none(
            well_area=repair.well_area,
            well_number=repair.well_number,
            begin_time=repair.begin_time,
        )
        if repair_info:
            return repair_info
    except SQLAlchemyError as db_err:
        msg = f"Database Exception RepairTima {db_err}"
        logger.error(msg, extra={" repair_id": repair_info})
        raise ExceptionError(msg)
    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg, extra={" repair_id": repair_info})
        raise ExceptionError(msg)

@router.get("/find_by_id")
@version(1)
async def find_by_id(repair_id: int, user: Users = Depends(get_current_user)):
    try:
        repair_info = await RepairDataDAO.find_one_or_none(id=repair_id)
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


@router.put("/update")
@version(1)
async def update_repair_time(
        repair_info: SRepairTimeClose = Depends(),
        repair: SRepairTime = Depends(find_by_id),
        user: Users = Depends(get_current_user)
):
    try:
        result = await RepairDataDAO.update_data(
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


@router.delete("/delete")
@version(1)
async def delete_brigade(
        repair: SRepairTime = Depends(find_by_id),
        user: Users = Depends(get_current_user)
):
    try:

        return await RepairDataDAO.delete_item_all_by_filter(
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
