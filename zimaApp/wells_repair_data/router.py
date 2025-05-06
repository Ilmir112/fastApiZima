from fastapi import APIRouter

from zimaApp.wells_repair_data.dao import WellsRepairsDAO
from zimaApp.wells_repair_data.schemas import SWellsRepair
from fastapi_versioning import version

router = APIRouter(
    prefix="/wells_repair_router",
    tags=["Данные по планам работ"],
)


@router.get("/")
@version(1)
async def get_wells_repair() -> list[SWellsRepair]:
    result = await WellsRepairsDAO.find_all(SWellsRepair)
    return result
