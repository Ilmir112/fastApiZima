from fastapi import APIRouter, Depends
from datetime import date

from sqlalchemy.exc import SQLAlchemyError

from zimaApp.logger import logger
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
    prefix="/brigade_router",
    tags=["Данные бригадам"],
)


class BrigadeSearch:
    def __init__(self, number_brigade: int, contractor: str):
        self.number_brigade = number_brigade
        self.contractor = contractor


@router.get("/find_well_repairs_brigade_by_filter/")
@version(1)
async def find_brigade_one(brigade: BrigadeSearch = Depends()):
    result = await BrigadeDAO.find_one_or_none(
        number_brigade=brigade.number_brigade, contractor=brigade.contractor
    )
    return result


@router.post("/add_wells_data")
@version(1)
async def add_wells_data(
    brigade_info: SWellsBrigade, user: Users = Depends(get_current_user)
):
    try:
        if brigade_info:
            await delete_brigade(brigade_info)
            result = await BrigadeDAO.add_data(
                id=brigade_info.id,
                contractor=brigade_info.contractor,
                costumer=brigade_info.costumer,
                expedition=brigade_info.expedition,
                number_brigade=brigade_info.number_brigade,
                brigade_master=brigade_info.brigade_master,
                phone_number_brigade=brigade_info.phone_number_brigade,
                lifting_unit=brigade_info.lifting_unit,
                hydraulic_wrench=brigade_info.hydraulic_wrench,
                weight_indicator=brigade_info.weight_indicator,
                brigade_composition=brigade_info.brigade_composition,
                pvo_type=brigade_info.pvo_type,
                number_pvo=brigade_info.number_pvo,
            )

            await TelegramInfo.send_message_create_brigade(
                user.login_user, brigade_info.number_brigade, brigade_info.contractor
            )

            return {"status": "success", "id": result}

    except SQLAlchemyError as db_err:
        msg = f"Database Exception Brigade {db_err}"
        logger.error(
            msg,
            extra={
                "number_brigade": brigade_info.number_brigade,
                "contractor": brigade_info.contractor,
            },
            exc_info=True,
        )

    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(
            msg,
            extra={
                "number_brigade": brigade_info.number_brigade,
                "contractor": brigade_info.contractor,
            },
            exc_info=True,
        )


@router.put("/update")
@version(1)
async def update_brigade_data(
    brigade: SWellsBrigade, user: Users = Depends(get_current_user)
):
    try:
        data = await find_brigade_one(brigade)
        if data:
            result = await WellsDatasDAO.update_data(
                data.id,
                id=brigade.id,
                contractor=brigade.contractor,
                costumer=brigade.costumer,
                expedition=brigade.expedition,
                number_brigade=brigade.number_brigade,
                brigade_master=brigade.brigade_master,
                phone_number_brigade=brigade.phone_number_brigade,
                lifting_unit=brigade.lifting_unit,
                hydraulic_wrench=brigade.hydraulic_wrench,
                weight_indicator=brigade.weight_indicator,
                brigade_composition=brigade.brigade_composition,
                pvo_type=brigade.pvo_type,
                number_pvo=brigade.number_pvo,
            )

            await TelegramInfo.send_message_update_brigade(
                user.login_user, brigade.number_brigade, brigade.contractor
            )

            return result
    except SQLAlchemyError as db_err:
        msg = f"Database Exception Brigade {db_err}"
        logger.error(
            msg,
            extra={
                "number_brigade": brigade.number_brigade,
                "contractor": brigade.contractor,
            },
            exc_info=True,
        )

    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(
            msg,
            extra={
                "number_brigade": brigade.number_brigade,
                "contractor": brigade.contractor,
            },
            exc_info=True,
        )


@router.delete("/delete_brigade")
@version(1)
async def delete_brigade(
    brigade: SWellsBrigade = Depends(), user: Users = Depends(get_current_user)
):
    data = await find_brigade_one(brigade)
    if data:
        return await BrigadeDAO.delete_item_all_by_filter(
            number_brigade=brigade.number_brigade, contractor=brigade.contractor
        )
