from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError


from zimaApp.logger import logger
from zimaApp.tasks.telegram_bot_template import TelegramInfo
from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users
from zimaApp.gnkt_data.dao import GnktDatasDAO
from zimaApp.gnkt_data.schemas import SGnktData
from fastapi_versioning import version

router = APIRouter(
    prefix="/gnkt_data_router",
    tags=["Данные по ГНКТ"],
)


@router.get("/find_gnkt_data_all")
@version(1)
async def find_gnkt_data_all():
    try:
        result = await GnktDatasDAO.find_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error {e}")

    return result


@router.get("/find_gnkt_data_by_gnkt")
@version(1)
async def find_gnkt_data(gnkt_number):
    try:
        result = await GnktDatasDAO.find_all(gnkt_number=gnkt_number)
        result = sorted(result, key=lambda k: k.date_repair, reverse=True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error {e}")

    return result


@router.get("/find_gnkt_data_by_well_number")
@version(1)
async def find_gnkt_data(well_number, well_area, date_repair):
    try:
        result = await GnktDatasDAO.find_one_or_none(
            well_number=well_number,
            well_area=well_area,
            date_repair=datetime.strptime(date_repair, "%Y-%m-%d").date(),
        )
    except Exception as e:
        logger.critical(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return result


@router.post("/add_data")
@version(1)
async def add_wells_data(gnkt_data: SGnktData, user: Users = Depends(get_current_user)):
    print(gnkt_data)
    data = await GnktDatasDAO.find_one_or_none(
        well_number=gnkt_data.well_number,
        well_area=gnkt_data.well_area,
        date_repair=gnkt_data.date_repair,
        contractor=user.contractor,
    )
    print(data)
    if data:
        await delete_well_by_type_kr_and_date_create(
            gnkt_data.well_number,
            gnkt_data.well_area,
            gnkt_data.date_repair,
            data.contractor,
        )

    try:
        result = await GnktDatasDAO.add_data(
            gnkt_number=gnkt_data.gnkt_number,
            well_number=gnkt_data.well_number,
            well_area=gnkt_data.well_area,
            contractor=user.contractor,
            length_gnkt=gnkt_data.length_gnkt,
            diameter_gnkt=gnkt_data.diameter_gnkt,
            wear_gnkt=gnkt_data.wear_gnkt,
            mileage_gnkt=gnkt_data.mileage_gnkt,
            tubing_fatigue=gnkt_data.tubing_fatigue,
            previous_well=gnkt_data.previous_well,
            date_repair=gnkt_data.date_repair,
            pvo_number=gnkt_data.pvo_number,
        )
        await TelegramInfo.send_message_create_plan_gnkt(
            user.login_user, gnkt_data.well_number, gnkt_data.well_area
        )

        return {"status": "success", "id": result}
    except SQLAlchemyError as db_err:
        msg = f"Database Exception Brigade {db_err}"
        logger.error(
            msg,
            extra={
                "gnkt_brigade": gnkt_data.gnkt_number,
                "well_number": gnkt_data.well_number,
            },
            exc_info=True,
        )

    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(
            msg,
            extra={
                "gnkt_brigade": gnkt_data.gnkt_number,
                "well_number": gnkt_data.well_number,
            },
            exc_info=True,
        )


@router.delete("/delete_well")
@version(1)
async def delete_well_by_type_kr_and_date_create(
    well_number: str,
    well_area: str,
    date_repair: date,
    contractor: str,
    user: Users = Depends(get_current_user),
):

    return await GnktDatasDAO.delete_item_all_by_filter(
        well_number=well_number,
        well_area=well_area,
        date_repair=date_repair,
        contractor=contractor,
    )
