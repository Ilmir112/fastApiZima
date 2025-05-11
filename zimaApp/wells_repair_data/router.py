from fastapi import APIRouter, Depends, BackgroundTasks

from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users
from zimaApp.wells_repair_data.dao import WellsRepairsDAO
from zimaApp.wells_repair_data.schemas import SWellsRepair, SNewWellDatas
from fastapi_versioning import version

router = APIRouter(
    prefix="/wells_repair_router",
    tags=["Данные по планам работ"],
)
class WellsSearchArgs:
    def __init__(self, well_number: str, well_area: str, type_kr: str, date_create: str):
        self.well_number = well_number
        self.well_area = well_area
        self.type_kr = type_kr
        self.date_create = date_create


@router.get("/find_well_repairs_by_filter/")
@version(1)
async def find_wells_in_silencing_for_region(wells_data: WellsSearchArgs = Depends()):
    result = await WellsRepairsDAO.find_all(
        well_number=wells_data.well_number, deposit_area=wells_data.well_area,
        type_kr=wells_data.type_kr, date_create=wells_data.date_create
    )
    return result


@router.post("/add_wells_data")
@version(1)
async def add_wells_data(
    well_repair: SWellsRepair,
    well_data: SNewWellDatas,
    user: Users = Depends(get_current_user),
):
    result = await WellsRepairsDAO.add_data(
        wells_id=well_data.wells_id,
        category_dict=well_repair.category_dict,
        type_kr=well_repair.type_kr,
        work_plan=well_repair.work_plan,
        excel_json=well_repair.excel_json,
        data_change_paragraph=well_repair.data_change_paragraph,
        geolog_id=user.id,
        date_create=well_repair.date_create
    )
    return {"status": "success", "id": result}
