from celery.bin.result import result
from fastapi import APIRouter, Depends
from datetime import date, datetime

from sqlalchemy.exc import SQLAlchemyError

from zimaApp.brigade.models import Brigade
from zimaApp.brigade.router import find_brigade_by_id
from zimaApp.brigade.schemas import SBrigadeSearch
from zimaApp.exceptions import ExceptionError, WellsAlreadyExistsException, BrigadeAlreadyExistsException, \
    DowntimeDurationAlreadyExistsException
from zimaApp.logger import logger
from zimaApp.repairGis.schemas import RepairGisUpdate
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


@router.get("/find_all_works_by_id_summary")
@version(1)
async def find_all_works_by_id_summary(summary_id: int, user: Users = Depends(get_current_user)):
    try:
        wells = await RepairTimeDAO.find_one_or_none(id=summary_id)

        results = await BrigadeSummaryDAO.find_all(repair_time_id=summary_id)

        serialized_data = []
        if results:
            for data in results:
                time_enum_value = data.time_interval.value if hasattr(data.time_interval,
                                                                      'value') else data.time_interval

                serialized_data.append(
                    {
                        "id": data.id,
                        "Дата": f"{data.date_summary.strftime('%d.%m.%Y')} {time_enum_value}",
                        "Проведенные работы": data.work_details,
                        "примечание": data.notes,
                        "статус подписания": data.status_act,
                        "акт": data.act_path,
                        "фото": data.photo_path,
                        "видео": data.video_path,
                    })

            return sorted(serialized_data, key=lambda x: x["Дата"]), wells.well_id
    except SQLAlchemyError as db_err:
        msg = f"Database Exception Summary {db_err}"
        logger.error(msg, extra={"summary": summary_id})
        raise ExceptionError(msg)

    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg, extra={"summary": summary_id})
        raise ExceptionError(msg)



@router.put("/update")
async def update_repair_summary(
    repair_info: RepairGisUpdate, user: Users = Depends(get_current_user)
):
    try:
        repair_dict = repair_info.model_dump()
        if repair_info:
            result = await BrigadeSummaryDAO.update(
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

@router.post("/add_summary")
async def add_summary(work_details: str, work_data: SUpdateSummary,
        summary_info: BrigadeSummary = Depends(),
        user: Users = Depends(get_current_user)):

    try:
        if summary_info:
            result_date, result_time, result_interval = await RepairTimeDAO.get_date_and_interval(
            work_data.date_summary)
            summary =  await BrigadeSummaryDAO.find_one_or_none(time_interval=result_interval, date_summary=result_date, repair_time_id=summary_info)
            if summary:
                return
            result = await BrigadeSummaryDAO.add_data(
                date_summary=result_date,
                time_interval=result_interval,
                work_details = work_details,
                repair_time_id=summary_info,)
            return result
    except SQLAlchemyError as db_err:
        msg = f"Database Exception Summary {db_err}"
        logger.error(msg)
    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg)

@router.put("/update_summary")
@version(1)
async def update_summary_data(
        date_work: date,
        time_interval: TimeWorkEnum,
        summary_info: BrigadeSummary = Depends(find_all_works_by_id_summary),
        user: Users = Depends(get_current_user)
):
    try:
        result = await BrigadeSummaryDAO.update_data(
            summary_info.id,
            date=date_work,
            time_interval=time_interval,
            work_details=summary_info.time_interval)
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
