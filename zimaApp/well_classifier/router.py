from fastapi import APIRouter, Depends

from zimaApp.logger import logger
from zimaApp.well_classifier.dao import WellClassifierDAO
from zimaApp.well_classifier.schemas import (
    SWellsClassifierBatch,
    SWellsClassifierRegion,
)
from zimaApp.well_silencing.router import WellsSearchArgs
from fastapi_versioning import version
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(
    prefix="/wells_classifier",
    tags=["Классификатор скважин"],
)


@router.post("/find_well_classifier_all/")
@version(1)
async def find_well_classifier_all(wells_data: SWellsClassifierRegion):
    try:
        results = await WellClassifierDAO.find_all(region=wells_data.region)
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

    try:
        await delete_well_classifier_for_region(wells_data.data[0])

        for item in wells_data.data:
            try:
                await WellClassifierDAO.add_data(**item.dict())

            except SQLAlchemyError as db_err:
                results.append({"status": "error", "error": str(db_err), "item": item})
                logger.error(f'Database error while processing item {item}: {str(db_err)}', exc_info=True)
            except ValueError as val_err:
                results.append({"status": "error", "error": f'Value error: {str(val_err)}', "item": item})
                logger.error(f'Value error in item {item}: {str(val_err)}', exc_info=True)
            except TypeError as type_err:
                results.append({"status": "error", "error": f'Type error: {str(type_err)}', "item": item})
                logger.error(f'Type error in item {item}: {str(type_err)}', exc_info=True)
            except KeyError as key_err:
                results.append({"status": "error", "error": f'Key error: {str(key_err)}', "item": item})
                logger.error(f'Key error in item {item}: {str(key_err)}', exc_info=True)
            except Exception as e:
                results.append({"status": "error", "error": str(e), "item": item})
                logger.error(f'Unexpected error in item {item}: {str(e)}', exc_info=True)

        logger.info(f'Добавлено {len(results)} скважин', exc_info=True)

    except SQLAlchemyError as db_err:
        msg = f'Database Exception {db_err}'
        logger.error(msg, extra={"well_number": wells_data.well_number, "deposit_area": wells_data.deposit_area}, exc_info=True)
    except Exception as e:
        msg = f'Unexpected error: {str(e)}'
        logger.error(msg, extra={"well_number": wells_data.well_number, "deposit_area": wells_data.deposit_area}, exc_info=True)

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
