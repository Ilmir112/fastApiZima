import json

from fastapi import APIRouter, Depends, HTTPException
from datetime import date, datetime

from sqlalchemy.exc import SQLAlchemyError

from zimaApp.logger import logger
from zimaApp.tasks.telegram_bot_template import TelegramInfo

from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users
from zimaApp.well_silencing.router import WellsSearchArgs
from zimaApp.wells_data.dao import WellsDatasDAO
from zimaApp.wells_data.router import find_wells_data
from zimaApp.wells_data.schemas import SWellsData
from zimaApp.wells_repair_data.dao import WellsRepairsDAO
from zimaApp.wells_repair_data.schemas import SWellsRepair
from fastapi_versioning import version

router = APIRouter(
    prefix="/wells_repair_router",
    tags=["Данные по планам работ"],
)


class WellsSearchRepair:
    def __init__(self, type_kr: str | None, work_plan: str | None, date_create: date | None, wells_id: int):
        self.type_kr = type_kr
        self.date_create = date_create
        self.work_plan = work_plan
        self.wells_id = wells_id


@router.get("/find_well_repairs_by_filter/")
@version(1)
async def find_wells_in_repairs(
        wells_data: WellsSearchArgs = Depends(),
        user: Users = Depends(get_current_user)
):
    result = await WellsRepairsDAO.find_one_or_none(
        type_kr=wells_data.type_kr, date_create=wells_data.date_create, work_plan=wells_data.work_plan,
        wells_id=wells_data.wells_id
    )

    return result


@router.get("/find_work_plan_all/")
@version(1)
async def find_work_plan_all(user: Users = Depends(get_current_user)):
    result = await WellsRepairsDAO.find_all(1)
    return result


@router.get("/find_repair_filter_by_number")
@version(1)
async def find_repair_filter_by_number(well_number: str, user: Users = Depends(get_current_user)):
    try:
        # Используем новый метод DAO для получения объединенных данных
        joined_data = await WellsDatasDAO.find_wells_with_repairs(
            well_number=well_number,
            contractor_id=user.contractor
        )
        if joined_data:
            # Преобразуем каждый кортеж в словарь с понятными ключами
            keys = ['Номер скважины', 'площадь', 'КР', 'вид ПР', 'Дата создания', 'id']
            serialized_data = [
                dict(zip(keys, row))
                for row in joined_data
            ]
            print(serialized_data)
            return serialized_data
        else:
            return None
    except Exception as e:
        logger.error("error message", extra=e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/find_well_filter_by_number")
@version(1)
async def find_well_filter_by_number(
        joined_data=Depends(find_repair_filter_by_number)):
    try:
        result_list = []
        if joined_data:
            for row in joined_data:
                result_list.append(f'{row["Номер скважины"]} '
                                   f'{row["площадь"]} '
                                   f'{row["КР"]} '
                                   f'{row["вид ПР"]} от '
                                   f'{row["Дата создания"]} '
                                   f'{row["id"]}')
            if result_list:
                return {"ремонты": result_list}

    except Exception as e:
        logger.error("error message", extra=e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/find_repair_id")
@version(1)
async def find_repair_id(
        id: int,
        user: Users = Depends(get_current_user)
):
    try:
        result = await WellsRepairsDAO.find_one_or_none(id=id)
        if result:
            return result
        else:
            return {"status": "not_found", "message": "Запись не найдена"}

    except SQLAlchemyError as db_err:
        logger.error(f'Database error occurred: {str(db_err)}', exc_info=True)
        return {"status": "error", "message": "Ошибка базы данных"}

    except Exception as e:
        logger.error(f'Unexpected error occurred: {str(e)}', exc_info=True)
        return {"status": "error", "message": "Произошла неожиданная ошибка"}

@router.get("/find_well_id")
@version(1)
async def find_well_id(
        wells_repair: WellsSearchRepair = Depends(),
        wells_data: WellsSearchArgs = Depends(),
        user: Users = Depends(get_current_user)
):
    try:
        joined_data = await WellsDatasDAO.find_wells_with_repairs_one_or_none(
            well_number=wells_data.well_number,
            well_area=wells_data.well_area,
            type_kr=wells_repair.type_kr,
            date_create=wells_repair.date_create,
            work_plan=wells_repair.work_plan,
            contractor=user.contractor
        )

        if not joined_data is None:
            logger.info("Скважина найдена", extra={
                "well_number": joined_data.well_number,
                "well_area": joined_data.well_area},
                        exc_info=True)

            return joined_data

    except SQLAlchemyError as db_err:
        logger.error(f'Database error occurred: {str(db_err)}', exc_info=True)
        return {"status": "error", "message": "Ошибка базы данных"}

    except Exception as e:
        logger.error(f'Unexpected error occurred: {str(e)}', exc_info=True)
        return {"status": "error", "message": "Произошла неожиданная ошибка"}


@router.post("/add_wells_data")
@version(1)
async def add_wells_data(
        wells_repair: SWellsRepair,
        wells_data: WellsSearchArgs = Depends(),
        user: Users = Depends(get_current_user),

):
    try:
        wells_data = await WellsDatasDAO.find_one_or_none(
            well_number=wells_data.well_number, well_area=wells_data.well_area
        )
        if wells_data:
            await delete_well_by_type_kr_and_date_create(wells_data.id, user.contractor, wells_repair)
            result = await WellsRepairsDAO.add_data(
                wells_id=wells_data.id,
                category_dict=wells_repair.category_dict,
                type_kr=wells_repair.type_kr,
                work_plan=wells_repair.work_plan,
                excel_json=wells_repair.excel_json,
                data_change_paragraph=wells_repair.data_change_paragraph,
                norms_time=wells_repair.norms_time,
                chemistry_need=wells_repair.chemistry_need,
                geolog_id=user.id,
                date_create=wells_repair.date_create,
                perforation_project=wells_repair.perforation_project,
                type_absorbent=wells_repair.type_absorbent,
                static_level=wells_repair.static_level,
                dinamic_level=wells_repair.dinamic_level,
                expected_data=wells_repair.expected_data,
                curator=wells_repair.curator,
                region=wells_repair.region,
                contractor=user.contractor
            )

            await TelegramInfo.send_message_create_plan(user.login_user, wells_data.well_number,
                                                        wells_data.well_area, wells_repair.work_plan)

            return {"status": "success", "id": result}

    except SQLAlchemyError as db_err:
        msg = f'Database Exception {db_err}'
        logger.error(msg, extra={"well_number": wells_data.well_number,
                                 "well_area": wells_data.well_area}, exc_info=True)

    except Exception as e:
        msg = f'Unexpected error: {str(e)}'
        logger.error(msg, extra={"well_number": wells_data.well_number, "well_area": wells_data.well_area},
                     exc_info=True)


@router.delete("/delete_well")
@version(1)
async def delete_well_by_type_kr_and_date_create(wells_id: int, contractor: str,
                                                 wells_repair: WellsSearchRepair = Depends(),
                                                 user: Users = Depends(get_current_user)):
    data = await WellsRepairsDAO.find_one_or_none(
        type_kr=wells_repair.type_kr,
        date_create=wells_repair.date_create,
        work_plan=wells_repair.work_plan,
        wells_id=wells_id,
        contractor=contractor
    )
    if data:
        return await WellsRepairsDAO.delete_item_all_by_filter(
            type_kr=wells_repair.type_kr,
            date_create=wells_repair.date_create,
            work_plan=wells_repair.work_plan,
            wells_id=wells_id,
            contractor=contractor
        )
