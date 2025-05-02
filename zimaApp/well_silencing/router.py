from fastapi import APIRouter
from zimaApp.well_silencing.dao import WellSilencingDAO
from zimaApp.well_silencing.schemas import SWellsSilencing

router = APIRouter(
    prefix="/wells_silencing_router",
    tags=["Перечень скважин без глушения"],
)


@router.get("/")
async def get_wells_silencing() -> list[SWellsSilencing]:
    result = await WellSilencingDAO.find_all()
    return result
