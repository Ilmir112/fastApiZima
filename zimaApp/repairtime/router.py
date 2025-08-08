from fastapi import APIRouter, Depends

from sqlalchemy.exc import SQLAlchemyError

from zimaApp.brigade.models import Brigade
from zimaApp.brigade.router import find_brigade_by_id
from zimaApp.exceptions import ExceptionError, WellsAlreadyExistsException, BrigadeAlreadyExistsException
from zimaApp.logger import logger
from zimaApp.repairtime.dao import RepairTimeDAO
from zimaApp.repairtime.models import StatusSummary
from zimaApp.repairtime.schemas import SRepairTime, SRepairTimeClose
from zimaApp.summary.schemas import SUpdateSummary

from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users
from fastapi_versioning import version

from zimaApp.wells_data.models import WellsData
from zimaApp.wells_data.router import find_wells_data_by_id
from zimaApp.wells_repair_data.models import StatusWorkPlan

router = APIRouter(
    prefix="/repair_time",
    tags=["Сводная времени сводки"],
)

@router.get("/check_well_id_and_end_time")
@version(1)
async def check_well_id_and_end_time(well_id: int, user: Users = Depends(get_current_user)):
    try:
        result = await RepairTimeDAO.find_one_or_none(well_id=well_id, end_time=None)
        if result:
            return result
    except SQLAlchemyError as db_err:
        msg = f"Database Exception Brigade {db_err}"
        logger.error(msg, exc_info=True)
    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg, exc_info=True)
        raise ExceptionError(msg)


@router.get("/check_brigade_id_and_end_time")
@version(1)
async def check_brigade_id_and_end_time(brigade_id: int, user: Users = Depends(get_current_user)):
    try:
        result = await RepairTimeDAO.find_one_or_none(brigade_id=brigade_id, end_time=None)
        if result:
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
        result =  await RepairTimeDAO.find_by_id_repair(summary_id)
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

@router.post("/add")
@version(1)
async def add_data(
        summary_info: SUpdateSummary,
        well_data: WellsData=Depends(find_wells_data_by_id),
        brigade: Brigade=Depends(find_brigade_by_id),
        user: Users = Depends(get_current_user)
):

    check_wells = await check_well_id_and_end_time(well_data.id)
    if check_wells:
        raise WellsAlreadyExistsException

    check_brigade = await check_brigade_id_and_end_time(brigade.id)
    if check_brigade:
        raise BrigadeAlreadyExistsException
    try:
        if summary_info:
            result_date, result_time, result_interval = await RepairTimeDAO.get_date_and_interval(
                summary_info.date_summary)

            summary_data = {
                "date_summary": result_date,
                "time_interval": result_interval,
                "work_details": summary_info.work_details,
                "notes": None,
                "act_path": None,
                "status_act": StatusWorkPlan.NOT_SIGNED,
                "photo_path": None,
                "video_path": None
            }

            repair_data = {
                'well_id': well_data.id,
                'start_time': summary_info.date_summary,
                'end_time': None,
                "brigade_id": brigade.id
            }

            result = await RepairTimeDAO.add_brigade_with_repairs(summary_data, repair_data)
            if result:
                return {"status": "success", "id": result}

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




@router.get("/find_all_by_filter_status")
@version(1)
async def find_all_by_filter_open( user: Users = Depends(get_current_user)):
    try:
        repair = await RepairTimeDAO.find_all(status=StatusSummary.OPEN)
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
