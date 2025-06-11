from fastapi import APIRouter, Depends
from datetime import date, datetime

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

from zimaApp.wells_repair_data.dao import WellsRepairsDAO
from zimaApp.wells_repair_data.router import WellsSearchRepair, find_wells_in_repairs, find_well_id
from zimaApp.wells_repair_data.schemas import SWellsRepair

router = APIRouter(
    prefix="/norms_work",
    tags=["Данные по нормированию ремонта"],
)


class NormSearchId:
    def __init__(self, id: int, contractor: str):
        self.id = id
        self.contractor = contractor


@router.get("/find_well_filter_by_number")
@version(1)
async def find_well_filter_by_number(well_number: str, user: Users = Depends(get_current_user)):
    try:
        result_list =[]
        wells = await WellsDatasDAO.find_all(well_number=well_number, contractor=user.contractor)
        if wells:
            for well in wells:
                repair_well = await WellsRepairsDAO.find_all(wells_id=well.id)
                if repair_well:
                    for repair in repair_well:
                        result = await NormDAO.find_all(repair_id=repair.id)
                        if result:
                            for norms in result:
                                result_list.append(f'{well.well_number} '
                                                   f'{well.well_area} '
                                                   f'{repair.type_kr}'
                                                   f' {repair.work_plan} от '
                                                   f'{norms.date_create} {norms.id}')
            if result_list:
                return {"ремонты": result_list}
    except Exception as e:
        logger.error(e)



@router.get("/find_norms_by_filter/")
@version(1)
async def find_norms_one(
        wells_repair: WellsSearchRepair = Depends(find_wells_in_repairs)):

    result = await NormDAO.find_one_or_none(
        wells_id=wells_repair.wells_id)
    return result


@router.get("/find_norms_by_id/")
@version(1)
async def find_norms_one(norms: NormSearchId = Depends(), user: Users = Depends(get_current_user)):
    if norms.contractor == user.contractor:
        result = await NormDAO.find_one_or_none(
            id=norms.id)
    return result


@router.get("/find_norms_all/")
@version(1)
async def find_norms_all():
    result = await NormDAO.find_all()
    return result


@router.post("/add_norm")
@version(1)
async def add_norm_data(
        norms: SNorms,
        repair_wells: WellsSearchRepair = Depends(),
        user: Users = Depends(get_current_user)
):
    repair_wells = await WellsRepairsDAO.find_one_or_none(
            type_kr=repair_wells.type_kr,
            date_create=repair_wells.date_create,
            work_plan=repair_wells.work_plan,
            contractor=user.contractor,
            wells_id=repair_wells.wells_id
        )

    try:
        if norms and repair_wells:
            await delete_norms(norms)
            result = await NormDAO.add_data(
                repair_id=repair_wells.id,
                start_well_repair=norms.start_well_repair,
                repair_well_repair=norms.repair_well_repair,
                type_tkrs=norms.type_tkrs.value,
                summary_work=norms.summary_work,
                norms_json=norms.norms_json,
                lifting_unit=norms.lifting_unit,
                creater_id=user.id,
                number_brigade=norms.number_brigade,
                norms_time=norms.norms_time
            )
            if result:
                await TelegramInfo.send_message_create_norms(user.login_user, norms.repair_id)

                return {"status": "success", "id": result}

    except SQLAlchemyError as db_err:
        msg = f'Database Exception Brigade {db_err}'
        logger.error(msg, extra={"repair_id": norms.repair_id}, exc_info=True)

    except Exception as e:
        msg = f'Unexpected error: {str(e)}'
        logger.error(msg, extra={"repair_id": norms.repair_id}, exc_info=True)


@router.put("/update")
@version(1)
async def update_brigade_data(norms: SNorms,
        repair_wells: WellsSearchRepair = Depends(find_well_id),
                              user: Users = Depends(get_current_user)):
    try:

        if repair_wells:
            result = await NormDAO.update_data(id=norms.id,
                repair_id=repair_wells.id,
                start_well_repair=norms.start_well_repair,
                repair_well_repair=norms.repair_well_repair,
                type_tkrs=norms.type_tkrs,
                summary_work=norms.summary_work,
                norms_json=norms.norms_json,
                lifting_unit=norms.lifting_unit,
                creater_id=user.id,
                number_brigade=norms.number_brigade,
                norms_time=norms.norms_time,
                date_create=norms.date_create)

            await TelegramInfo.send_message_update_brigade(user.login_user, norms.number_brigade,
                                                           user.contractor)

            return result
    except SQLAlchemyError as db_err:
        msg = f'Database Exception Brigade {db_err}'
        logger.error(msg, extra={"number_brigade": norms.number_brigade,
                                 "contractor": user.contractor}, exc_info=True)

    except Exception as e:
        msg = f'Unexpected error: {str(e)}'
        logger.error(msg, extra={"number_brigade": norms.number_brigade,
                                 "contractor": user.contractor}, exc_info=True)

@router.delete("/delete_norm")
@version(1)
async def delete_norms(
        norms: SNorms,
        user: Users = Depends(get_current_user)):
    data = await NormDAO.find_one_or_none(repair_id=norms.repair_id, start_well_repair=norms.start_well_repair)
    if data:
        return await NormDAO.delete_item_all_by_filter(repair_id=norms.repair_id, start_well_repair=norms.start_well_repair)