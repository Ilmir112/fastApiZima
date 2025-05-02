from fastapi import APIRouter
from zimaApp.database import async_session_maker

from zimaApp.well_classifier.schemas import SWellClassifier
from zimaApp.well_classifier.models import WellClassifier
from sqlalchemy import select

router = APIRouter(
    prefix="/wells_classifier",
    tags=["Классификатор скважин"],
)
@router.get("/")
async def get_wells_classifier() -> list[SWellClassifier]:
    result = await SWellClassifier.find_all()
    return result

