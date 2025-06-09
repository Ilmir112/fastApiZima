from fastapi import APIRouter, Depends
from datetime import date

from sqlalchemy.exc import SQLAlchemyError

from zimaApp.logger import logger
from zimaApp.norms.dao import NormDAO
from zimaApp.tasks.telegram_bot_template import TelegramInfo

from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users
from zimaApp.well_silencing.router import WellsSearchArgs
from zimaApp.wells_data.dao import WellsDatasDAO
from zimaApp.wells_data.router import find_wells_data
from zimaApp.wells_data.schemas import SWellsData
from zimaApp.brigade.dao import BrigadeDAO
from zimaApp.norms.schemas import SNorms
from fastapi_versioning import version

from zimaApp.wells_repair_data.router import WellsSearchRepair, find_wells_in_repairs

router = APIRouter(
    prefix="/norms_work",
    tags=["Данные по нормированию ремонта"],
)


class BrigadeSearch:
    def __init__(self, number_brigade: int, contractor: str):
        self.number_brigade = number_brigade
        self.contractor = contractor


@router.get("/find_norms_by_filter/")
@version(1)
async def find_norms_one(brigade: BrigadeSearch = Depends(), wells_repair: WellsSearchRepair = Depends(find_wells_in_repairs)):
    result = await NormDAO.find_one_or_none(
        number_brigade=brigade.number_brigade,
        contractor=brigade.contractor,
        wells_id=wells_repair.wells_id)
    return result


@router.post("/add_norm")
@version(1)
async def add_norm_data(
        norms: SNorms,
        user: Users = Depends(get_current_user)
):
    try:
        if norms:
            await delete_norms(number_brigade=norms.number_brigade, contractor=norms.contractor)
            result = await NormDAO.add_data(
                id=norms.id,
                repair_id=norms.repair_id,
                start_well_repair=norms.start_well_repair,
                repair_well_repair=norms.repair_well_repair,
                type_tkrs=norms.type_tkrs,
                summary_work=norms.brigade_master,
                norms_json=norms.norms_json,
                lifting_unit=norms.lifting_unit,
                creater_id=user.id,
                date_create=norms.date_create
            )

            await TelegramInfo.send_message_create_norms(user.login_user, norms.repair_id)

            return {"status": "success", "id": result}

    except SQLAlchemyError as db_err:
        msg = f'Database Exception Brigade {db_err}'
        logger.error(msg, extra={"repair_id": norms.repair_id}, exc_info=True)

    except Exception as e:
        msg = f'Unexpected error: {str(e)}'
        logger.error(msg, extra={"repair_id": norms.repair_id}, exc_info=True)


@router.delete("/delete_norm")
@version(1)
async def delete_norms(norms: SNorms, user: Users = Depends(get_current_user)):
    data = await find_norms_one(repair_id=norms.repair_id)
    if data:
        return await NormDAO.delete_item_all_by_filter(repair_id=norms.repair_id)
