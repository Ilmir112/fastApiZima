from fastapi import APIRouter, Depends, Query

from zimaApp.well_silencing.dao import WellSilencingDAO
from zimaApp.well_silencing.schemas import SWellsSilencing


class WellsSearchArgs:
    def __init__(
            self,
            well_number: str,
            well_area: str
    ):
        self.well_number = well_number
        self.well_area = well_area

router = APIRouter(
    prefix="/wells_silencing_router",
    tags=["Перечень скважин без глушения"],
)


@router.get("/find_well_silencing_all/")
async def get_wells_silencing() -> list[SWellsSilencing]:
    result = await WellSilencingDAO.find_all()
    return result


@router.post("/add_data_well_silencing")
async def add_data_well_silencing(wells_data: SWellsSilencing):
    return await WellSilencingDAO.add_data(
        well_number=wells_data.well_number,
        deposit_area=wells_data.deposit_area,
        today=wells_data.today,
        region=wells_data.region,
        costumer=wells_data.costumer
        )


@router.post("/delete_well_silencing")
async def delete_well_silencing_for_region(wells_data: SWellsSilencing):
    data = await WellSilencingDAO.find_all(region=wells_data.region)
    if data:
        return await WellSilencingDAO.delete_item(
            region=wells_data.region
            )



@router.get("/find_well_silencing/")
async def find_wells_in_silencing_for_region(
    well_number: str = Query(None),
    deposit_area: str = Query(None)
):
    result = await WellSilencingDAO.find_one_or_none(
        well_number=well_number,
        deposit_area=deposit_area
    )
    return result





