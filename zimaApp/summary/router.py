from fastapi import APIRouter, Depends
from datetime import date

from sqlalchemy.exc import SQLAlchemyError

from zimaApp.brigade.models import Brigade
from zimaApp.brigade.router import find_brigade_by_id
from zimaApp.brigade.schemas import SBrigadeSearch
from zimaApp.exceptions import ExceptionError, WellsAlreadyExistsException, BrigadeAlreadyExistsException
from zimaApp.logger import logger
from zimaApp.repairtime.dao import RepairTimeDAO
from zimaApp.repairtime.models import StatusSummary
from zimaApp.repairtime.schemas import SRepairTime
from zimaApp.summary.dao import BrigadeSummaryDAO
from zimaApp.summary.models import BrigadeSummary, TimeWorkEnum
from zimaApp.summary.schemas import SBrigadeSummary, SUpdateSummary
from zimaApp.tasks.telegram_bot_template import TelegramInfo

from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users

from zimaApp.brigade.dao import BrigadeDAO
from fastapi_versioning import version

from zimaApp.wells_data.models import WellsData
from zimaApp.wells_data.router import find_wells_data_by_id
from zimaApp.wells_repair_data.models import StatusWorkPlan

router = APIRouter(
    prefix="/summary",
    tags=["Данные по работам бригад"],
)




@router.get("/find_by_id_repair")
@version(1)
async def find_by_id_repair(summary_id: int, user: Users = Depends(get_current_user)):
    try:
        result =  await BrigadeSummaryDAO.find_by_id_repair(summary_id)
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


@router.put("/update_summary")
@version(1)
async def update_summary_data(
        date_work: date,
        time_interval: TimeWorkEnum,
        summary_info: BrigadeSummary = Depends(find_by_id_repair),
        user: Users = Depends(get_current_user)
):
    try:
        result = await BrigadeSummaryDAO.update_data(
                summary_info.id,
                date=data.date,
                time_interval=time_interval,
                work_details=data.time_interval)
        if result:
            logger.info(f"Добавлены данные в базу {summary_info.id} ")
            return result
    except SQLAlchemyError as db_err:
        msg = f"Database Exception Brigade {db_err}"
        logger.error(
            msg,
            extra={
                "id": result.id
            },
            exc_info=True,
        )

    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(
            msg,
            extra={
                "id": result.id
            },
            exc_info=True,
        )


@router.delete("/delete")
@version(1)
async def delete_brigade(
    brigade_id: int, user: Users = Depends(get_current_user)
):
    try:
        return await BrigadeSummaryDAO.delete_item_all_by_filter(
            id=brigade_id
        )
    except SQLAlchemyError as db_err:
        msg = f"Database Exception Brigade {db_err}"
        logger.error(msg, extra={"id": brigade_id})
        raise ExceptionError(msg)
    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg, extra={"id": brigade_id})
        raise ExceptionError(msg)
