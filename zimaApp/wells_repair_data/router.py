from fastapi import APIRouter, Depends, BackgroundTasks
from datetime import date

from sqlalchemy.exc import SQLAlchemyError

from zimaApp import logger
from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users
from zimaApp.well_silencing.router import WellsSearchArgs
from zimaApp.wells_data.dao import WellsDatasDAO
from zimaApp.wells_data.router import find_wells_data, find_id_wells_data
from zimaApp.wells_data.schemas import SWellsData
from zimaApp.wells_repair_data.dao import WellsRepairsDAO
from zimaApp.wells_repair_data.schemas import SWellsRepair, SNewWellDatas
from fastapi_versioning import version

router = APIRouter(
    prefix="/wells_repair_router",
    tags=["Данные по планам работ"],
)


class WellsSearchRepair:
    def __init__(self, type_kr: str | None, work_plan: str | None, date_create: date | None):
        self.type_kr = type_kr
        self.date_create = date_create
        self.work_plan = work_plan


@router.get("/find_well_repairs_by_filter/")
@version(1)
async def find_wells_in_repairs(wells_data: WellsSearchRepair = Depends()):
    result = await WellsRepairsDAO.find_one_or_none(
        type_kr=wells_data.type_kr, date_create=wells_data.date_create, work_plan=wells_data.work_plan
    )
    return result


@router.get("/find_well_filter_by_number")
@version(1)
async def find_well_id(well_number: str):
    try:
        data = await WellsDatasDAO.find_all(well_number=well_number)
        if data:
            result_list = []
            for wells in data:
                result = await WellsRepairsDAO.find_all(
                    wells_id=wells.id,
                )
                for wells_info in result:
                    result_list.append(f'{wells.well_number} '
                                       f'{wells.area_well} '
                                       f'{wells_info.type_kr}'
                                       f' {wells_info.work_plan} от '
                                       f'{wells_info.date_create}')
            if result_list:
                return {"ремонты": result_list}

    except Exception as e:
        asdwd = e
        print(e)


@router.get("/find_well_id")
@version(1)
async def find_well_id(
    wells_data: WellsSearchArgs = Depends(find_id_wells_data),
    wells_repair: WellsSearchRepair = Depends(find_wells_in_repairs),
    user_contrator: Users = Depends(get_current_user)
):
    try:
        result = await WellsRepairsDAO.find_one_or_none(
            wells_id=wells_data.id,
            type_kr=wells_repair.type_kr,
            date_create=wells_repair.date_create,
            work_plan=wells_repair.work_plan,
            geolog_id=user_contrator.id,
            contractor=user_contrator.contrator
        )
        if result is None:
            logger.info("Скважина найдена", extra={
                "well_number": wells_data.well_number,
                "deposit_area": wells_data.well_area},
                exc_info=True)
            return {"status": "not_found", "message": "Скважина не найдена"}
        return {"status": "success", "data": result}

    except SQLAlchemyError as db_err:
        logger.error(f'Database error occurred: {str(db_err)}', exc_info=True)
        return {"status": "error", "message": "Ошибка базы данных"}

    except Exception as e:
        logger.error(f'Unexpected error occurred: {str(e)}', exc_info=True)
        return {"status": "error", "message": "Произошла неожиданная ошибка"}



@router.post("/delete_well")
@version(1)
async def delete_well_by_type_kr_and_date_create(wells_repair: SWellsRepair, wells_id: int):
    data = await WellsRepairsDAO.find_all(
        type_kr=wells_repair.type_kr,
        date_create=wells_repair.date_create,
        work_plan=wells_repair.work_plan,
        wells_id=wells_id
    )
    if data:
        return await WellsRepairsDAO.delete_item_all_by_filter(
            type_kr=wells_repair.type_kr,
            date_create=wells_repair.date_create,
            work_plan=wells_repair.work_plan,
            wells_id=wells_id
        )


@router.post("/add_wells_data")
@version(1)
async def add_wells_data(
        wells_repair: SWellsRepair,
        user: Users = Depends(get_current_user),
        wells_data: SWellsData = Depends(find_wells_data)
):
    if wells_data:
        await delete_well_by_type_kr_and_date_create(wells_repair,
                                               wells_data.id)
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
            region=wells_repair.region
        )
        return {"status": "success", "id": result}
