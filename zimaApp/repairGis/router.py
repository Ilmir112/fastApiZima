from fastapi import APIRouter, Depends
from datetime import date

from sqlalchemy.exc import SQLAlchemyError

from zimaApp.logger import logger
from zimaApp.repairGis.dao import RepairsGisDAO
from zimaApp.repairGis.schemas import SRepairsGis, RepairGisUpdate
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
@router.get("/all")
@version(1)
async def get_repair_gis_all():
    try:
        repair_all = await RepairsGisDAO.find_all()
        return repair_all
    except SQLAlchemyError as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)

@router.post("/add_data")
@version(1)
async def add_wells_data(
        repair_info: SRepairsGis
):
    try:
        if repair_info:
            # await delete_brigade(repair_info)
            result = await RepairsGisDAO.add_data(
                status='открыт',
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
                image_pdf=repair_info.image_pdf,
            )

            await TelegramInfo.send_message_create_repair_gis(result)

            return {"status": "success", "id": result}

    except SQLAlchemyError as db_err:
        msg = f'Database Exception Brigade {db_err}'
        logger.error(msg, extra={"number_brigade": repair_info.well_id.well_number}, exc_info=True)

    except Exception as e:
        msg = f'Unexpected error: {str(e)}'
        logger.error(msg, extra={"number_brigade": repair_info.well_id.well_number}, exc_info=True)

@router.put("/update")
@version(1)
async def update_repair_gis_data(repair_info: RepairGisUpdate,
                              user: Users = Depends(get_current_user)):
    try:
        if repair_info:
            result = await RepairsGisDAO.update(id=repair_info.id, **repair_info.dict())

            # await TelegramInfo.send_message_update_brigade(user.login_user, repair_info.number_brigade,
            #                                                brigade.contractor)

            return result
    except SQLAlchemyError as db_err:
        msg = f'Database Exception Brigade {db_err}'
        logger.error(msg, extra={"number_brigade": repair_info.number_brigade,
                                 "contractor": repair_info.contractor}, exc_info=True)

    except Exception as e:
        msg = f'Unexpected error: {str(e)}'
        logger.error(msg, extra={"number_brigade": repair_info.number_brigade,
                                 "contractor": repair_info.contractor}, exc_info=True)


@router.delete("/delete_brigade")
@version(1)
async def delete_brigade(
        brigade: SWellsBrigade = Depends(),
        user: Users = Depends(get_current_user)):
    data = await RepairsGisDAO.find_one_or_none(brigade)
    if data:
        return await BrigadeDAO.delete_item_all_by_filter(
            number_brigade=brigade.number_brigade, contractor=brigade.contractor
        )
