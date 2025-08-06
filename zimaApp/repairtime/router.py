from fastapi import APIRouter, Depends

from sqlalchemy.exc import SQLAlchemyError

from zimaApp.exceptions import ExceptionError
from zimaApp.logger import logger
from zimaApp.repairtime.dao import RepairTimeDAO
from zimaApp.repairtime.schemas import SRepairTime, SRepairTimeClose

from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users
from fastapi_versioning import version

router = APIRouter(
    prefix="/repair_time",
    tags=["Сводная времени сводки"],
)

@router.post("/add")
@version(1)
async def add_wells_data(
    new_repair: SRepairTime, user: Users = Depends(get_current_user)
):
    try:
        if new_repair:
            await delete_brigade(new_repair)
            result = await RepairTimeDAO.add_data(
                brigade_id = new_repair.brigade_id,
                well_id = new_repair.well_id,
                brigade_summary_id = new_repair.brigade_summary_id,
                start_time = new_repair.start_time,
                end_time = new_repair.end_time
            )
            if result:
                return {"status": "success", "id": result}

    except SQLAlchemyError as db_err:
        msg = f"Database Exception Brigade {db_err}"
        logger.error(
            msg,
            extra={
                " brigade_summary_id": new_repair. brigade_summary_id
            },
            exc_info=True,
        )
        raise ExceptionError(msg)

    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(
            msg,
            extra={
                " brigade_summary_id": new_repair.brigade_summary_id
            },
            exc_info=True,
        )
        raise ExceptionError(msg)


@router.get("/find_all_by_filter_status")
@version(1)
async def find_all_by_filter_open( user: Users = Depends(get_current_user)):
    try:
        repair = RepairTimeDAO.find_all(filter_by={"end_time": None})
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

@router.get("/find_all")
@version(1)
async def find_all( user: Users = Depends(get_current_user)):
    try:
        repair = RepairTimeDAO.find_all()
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
        repair_info = RepairTimeDAO.find_one_or_none(id=repair_id)
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
        repair_info: SRepairTimeClose=Depends(),
        repair: SRepairTime=Depends(find_one_repair),
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


@router.delete("/delete")
@version(1)
async def delete_brigade(
        repair: SRepairTime=Depends(find_one_repair),
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
