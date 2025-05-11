from fastapi import APIRouter, Depends

from zimaApp.logger import logger
from zimaApp.well_classifier.dao import WellClassifierDAO
from zimaApp.well_classifier.schemas import (
    SWellsClassifierBatch,
    SWellsClassifierRegion,
)
from zimaApp.well_silencing.router import WellsSearchArgs
from fastapi_versioning import version

router = APIRouter(
    prefix="/wells_classifier",
    tags=["Классификатор скважин"],
)


@router.post("/find_well_classifier_all/")
@version(1)
async def find_well_classifier_all(wells_data: SWellsClassifierRegion):
    try:
        results = await WellClassifierDAO.find_all(region=wells_data.region, limit=10)
        if results:
            data = []
            for items in results:
                data.append(**items)
        results.append({"status": "success", "data": results})
    except Exception as e:
        data.append({"status": "error", "error": str(e), "item": items})
    return results


@router.post("/add_data_well_classifier")
@version(1)
async def add_data_well_classifier(wells_data: SWellsClassifierBatch):
    results = []
    region = wells_data.data[0].region

    await delete_well_classifier_for_region(wells_data.data[0])

    for item in wells_data.data:
        try:
            result = await WellClassifierDAO.add_data(**item.dict())
            results.append({"status": "success", "data": result})
        except Exception as e:
            results.append({"status": "error", "error": str(e), "item": item})
    logger.info("request handling time",
                extra={
                    "result append wells": len(results),
                })
    return results


@router.post("/delete_well_classifier")
@version(1)
async def delete_well_classifier_for_region(wells_data: SWellsClassifierRegion):
    data = await WellClassifierDAO.find_all(region=wells_data.region)
    if data:
        return await WellClassifierDAO.delete_item_all_by_filter(
            region=wells_data.region
        )


@router.get("/find_well_classifier/")
@version(1)
async def find_wells_in_silencing_for_region(wells_data: WellsSearchArgs = Depends()):
    result = await WellClassifierDAO.find_one_or_none(
        well_number=wells_data.well_number, deposit_area=wells_data.well_area
    )
    return result
