from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.testing.suite.test_reflection import users

from zimaApp.users.dependencies import get_current_user
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


@router.get("/find_gnkt_data")
@version(1)
async def find_gnkt_data(gnkt_number):
    result = await GnktDatasDAO.find_all(
        gnkt_number=gnkt_number
    )
    return result


@router.post("/add_data")
@version(1)
async def add_wells_data(gnkt_data: SGnktData):
    result = await GnktDatasDAO.add_data(
        gnkt_number=gnkt_data.gnkt_number,
        well_number=gnkt_data.well_number,
        well_area=gnkt_data.well_area,
        contractor=gnkt_data.contractor,
        diameter_gnkt=gnkt_data.length_gnkt,
        wear_gnkt=gnkt_data.diameter_gnkt,
        mileage_gnkt=gnkt_data.wear_gnkt,
        tubing_fatigue=gnkt_data.mileage_gnkt,
        previous_well=gnkt_data.tubing_fatigue,
        date_repair=gnkt_data.previous_well,
        pvo_number=gnkt_data.date_repair
    )
    return {"status": "success", "id": result}

