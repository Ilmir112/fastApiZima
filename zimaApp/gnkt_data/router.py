from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.testing.suite.test_reflection import users

from zimaApp.logger import logger
from zimaApp.users.models import Users
from zimaApp.well_silencing.router import WellsSearchArgs
from zimaApp.gnkt_data.dao import GnktDatasDAO
from zimaApp.gnkt_data.models import GnktData
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
        result = await GnktDatasDAO.find_all(
        )
    except Exception as e:
        raise HTTPException(e)
    return result


@router.get("/find_gnkt_data_by_gnkt")
@version(1)
async def find_gnkt_data(gnkt_number):
    try:
        result = await GnktDatasDAO.find_all(
            gnkt_number=gnkt_number
        )
    except Exception as e:
        raise HTTPException()
    return result


@router.get("/find_gnkt_data_by_well_number")
@version(1)
async def find_gnkt_data(well_number, well_area, date_repair):
    try:
        result = await GnktDatasDAO.find_one_or_none(
            well_number=well_number,
            well_area=well_area,
            date_repair=datetime.strptime(date_repair, "%Y-%m-%d").date()
        )
    except Exception as e:
        logger.critical(e)
        raise HTTPException(e)
    return result


@router.post("/add_data")
@version(1)
async def add_wells_data(gnkt_data: SGnktData):
    result = await GnktDatasDAO.add_data(
        gnkt_number=gnkt_data.gnkt_number,
        well_number=gnkt_data.well_number,
        well_area=gnkt_data.well_area,
        contractor=gnkt_data.contractor,
        length_gnkt=gnkt_data.length_gnkt,
        diameter_gnkt=gnkt_data.diameter_gnkt,
        wear_gnkt=gnkt_data.wear_gnkt,
        mileage_gnkt=gnkt_data.mileage_gnkt,
        tubing_fatigue=gnkt_data.tubing_fatigue,
        previous_well=gnkt_data.previous_well,
        date_repair=gnkt_data.date_repair,
        pvo_number=gnkt_data.pvo_number
    )
    return {"status": "success", "id": result}

