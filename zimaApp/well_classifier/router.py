from fastapi import APIRouter, Depends

from zimaApp.well_classifier.dao import WellClassifierDAO
from zimaApp.well_classifier.schemas import (SWellsClassifierBatch,
                                             SWellsClassifierRegion)
from zimaApp.well_silencing.router import WellsSearchArgs

router = APIRouter(
    prefix="/wells_classifier",
    tags=["Классификатор скважин"],
)


@router.get("/find_well_classifier_all/")
async def find_well_classifier_all(wells_data: SWellsClassifierRegion):
    result = await WellClassifierDAO.find_all(region=wells_data.region)
    return result


@router.post("/add_data_well_classifier")
async def add_data_well_classifier(wells_data: SWellsClassifierBatch):
    results = []
    for item in wells_data.data:

        try:
            result = await WellClassifierDAO.add_data(
                well_number=item.well_number,
                deposit_area=item.deposit_area,
                oilfield=item.oilfield,
                cdng=item.cdng,
                category_pressure=item.category_pressure,
                pressure_ppl=item.pressure_ppl,
                pressure_gst=item.pressure_gst,
                date_measurement=item.date_measurement,
                category_h2s=item.category_h2s,
                h2s_pr=item.h2s_pr,
                h2s_mg_l=item.h2s_mg_l,
                h2s_mg_m=item.h2s_mg_m,
                category_gf=item.category_gf,
                gas_factor=item.gas_factor,
                today=item.today,
                region=item.region,
                costumer=item.costumer,
            )
            results.append({"status": "success", "data": result})
        except Exception as e:
            results.append({"status": "error", "error": str(e), "item": item})
    return results


@router.post("/delete_well_classifier")
async def delete_well_silencing_for_region(wells_data: SWellsClassifierRegion):
    data = await WellClassifierDAO.find_all(region=wells_data.region)
    if data:
        return await WellClassifierDAO.delete_item_all_by_filter(
            region=wells_data.region
        )


@router.get("/find_well_classifier/")
async def find_wells_in_silencing_for_region(wells_data: WellsSearchArgs = Depends()):
    result = await WellClassifierDAO.find_one_or_none(
        well_number=wells_data.well_number, deposit_area=wells_data.well_area
    )
    return result
