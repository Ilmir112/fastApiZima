from fastapi import APIRouter
from zimaApp.database import async_session_maker
from zimaApp.well_classifier.dao import WellClassifierDAO
from zimaApp.wells_silencing.schemas import SWellsSilencing
from zimaApp.well_classifier.models import WellClassifier
from sqlalchemy import select

router = APIRouter(
    prefix="/wells_silencing",
    tags=["Перечень скважин без глушеия"],
)
@router.get("/")
async def get_well_classifier() -> list[SWellsSilencing]:
    result = await WellClassifierDAO.find_all()
    return result

