from fastapi import APIRouter, Depends, Query, Response


from zimaApp.well_silencing.dao import WellSilencingDAO
from zimaApp.well_silencing.schemas import SWellsSilencing, SWellsSilencingCreate, SWellsSilencingRegion, \
    SWellsSilencingBatch


class WellsSearchArgs:
    def __init__(
            self,
            well_number: str,
            well_area: str
    ):
        self.well_number = well_number
        self.well_area = well_area

# Обновляем модель для приема списка


router = APIRouter(
    prefix="/wells_silencing_router",
    tags=["Перечень скважин без глушения"],
)


@router.get("/find_well_silencing_all/")
async def find_well_silencing_all(wells_data: SWellsSilencingRegion):
    result = await WellSilencingDAO.find_all(region=wells_data.region)
    return result


@router.post("/add_data_well_silencing")
async def add_data_well_silencing(wells_data: SWellsSilencingBatch):
    results = []
    for item in wells_data.data:

        try:
            result = await WellSilencingDAO.add_data(
                well_number=item.well_number,
                deposit_area=item.deposit_area,
                today=item.today,
                region=item.region,
                costumer=item.costumer
            )
            results.append({"status": "success", "data": result})
        except Exception as e:
            results.append({"status": "error", "error": str(e), "item": item})
    return results


@router.post("/delete_well_silencing")
async def delete_well_silencing_for_region(wells_data: SWellsSilencingRegion):
    data = await WellSilencingDAO.find_all(region=wells_data.region)
    if data:
        return await WellSilencingDAO.delete_item_all_by_filter(
            region=wells_data.region
            )



@router.get("/find_well_silencing/")
async def find_wells_in_silencing_for_region(wells_data: WellsSearchArgs = Depends()
):
    result = await WellSilencingDAO.find_one_or_none(
        well_number=wells_data.well_number,
        deposit_area=wells_data.well_area
    )
    return result





