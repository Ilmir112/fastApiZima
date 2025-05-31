from fastapi import APIRouter, Depends, Query, Response

from starlette.responses import JSONResponse

from zimaApp.config import settings
from zimaApp.logger import logger
from zimaApp.well_silencing.dao import WellSilencingDAO
from zimaApp.well_silencing.schemas import (
    SWellsSilencing,
    SWellsSilencingBatch,
    SWellsSilencingCreate,
    SWellsSilencingRegion,
)
from fastapi_versioning import VersionedFastAPI, version
from fastapi_cache.decorator import cache


class WellsSearchArgs:
    def __init__(self, well_number: str, well_area: str | None):
        self.well_number = well_number
        self.well_area = well_area


# Обновляем модель для приема списка


router = APIRouter(
    prefix="/wells_silencing_router",
    tags=["Перечень скважин без глушения"],
)


@router.post("/find_well_silencing_all/")
# @cache(expire=1500)
@version(1)
async def find_well_silencing_all(wells_data: SWellsSilencingRegion):
    results = await WellSilencingDAO.find_all(region=wells_data.region)
    if results:
        data = []
        for r in results:
            data.append({
                "well_number": r.well_number,
                "well_area": r.well_area,
                "region": r.region,
                "today": r.today,
            })
        return results


@router.post("/find_well_silencing_all_one/")
# @cache(expire=1500)
@version(1)
async def find_well_silencing_all_one(wells_data: SWellsSilencingRegion):
    results = await WellSilencingDAO.find_first(region=wells_data.region)
    if results:
        return results


@router.post("/delete_well_silencing")
@version(1)
async def delete_well_silencing_for_region(wells_data: SWellsSilencingRegion):
    data = await WellSilencingDAO.find_all(region=wells_data.region)
    if data:
        return await WellSilencingDAO.delete_item_all_by_filter(
            region=wells_data.region
        )


@router.get("/find_well_silencing/")
@version(1)
async def find_wells_in_silencing_for_region(wells_data: WellsSearchArgs = Depends()):

    result = await WellSilencingDAO.find_one_or_none(
        well_number=wells_data.well_number, well_area=wells_data.well_area
    )
    return result


@router.post("/add_data_well_silencing")
@version(1)
async def add_data_well_silencing(wells_data: SWellsSilencingBatch):
    region = wells_data.data[0].region
    # find_result = await find_well_silencing_all(region)
    # if find_result:
    #     await delete_well_silencing_for_region(region)

    results = []
    for item in wells_data.data:
        try:
            result = await WellSilencingDAO.add_data(
                well_number=item.well_number,
                well_area=item.well_area,
                today=item.today,
                region=item.region,
                costumer=item.costumer,
            )
            results.append({"status": "success", "data": result})
        except Exception as e:
            results.append({"status": "error", "error": str(e), "item": item})
    return results
