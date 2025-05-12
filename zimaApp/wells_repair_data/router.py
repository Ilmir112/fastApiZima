from fastapi import APIRouter, Depends, BackgroundTasks
from datetime import date

from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users
from zimaApp.well_silencing.router import WellsSearchArgs
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
    def __init__(self, type_kr: str, work_plan: str, date_create: date):
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

@router.get("/find_well_id")
@version(1)
async def find_well_id(wells_data: WellsSearchArgs = Depends(find_id_wells_data),
                       wells_repair: WellsSearchRepair = Depends(find_wells_in_repairs)):

    result = await WellsRepairsDAO.find_all(
        wells_id=wells_data.id,
        type_kr=wells_repair.type_kr,
        date_create=wells_repair.date_create,
        work_plan=wells_repair.work_plan
    )
    return result





@router.post("/add_wells_data")
@version(1)
async def add_wells_data(
    well_repair: SWellsRepair,
    user: Users = Depends(get_current_user),
    wells_data: SWellsData = Depends(find_wells_data)
):
    if wells_data:
        result = await WellsRepairsDAO.add_data(
            wells_id=wells_data.id,
            category_dict=well_repair.category_dict,
            type_kr=well_repair.type_kr,
            work_plan=well_repair.work_plan,
            excel_json=well_repair.excel_json,
            data_change_paragraph=well_repair.data_change_paragraph,
            norms_time=well_repair.norms_time,
            chemistry_need=well_repair.chemistry_need,
            geolog_id=user.id,
            date_create=well_repair.date_create
        )
        return {"status": "success", "id": result}
