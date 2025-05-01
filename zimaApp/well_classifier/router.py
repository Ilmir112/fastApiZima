from fastapi import APIRouter
from zimaApp.database import async_session_maker
from zimaApp.well_classifier.models import WellClassifier
from sqlalchemy import select

router = APIRouter(
    prefix="/well_classifier",
    tags=["Классификатор скважин"],
)
@router.get("/")
async def get_well_classifier():
    async with async_session_maker() as session:
        query = select(WellClassifier)
        result  = await session.execute(query)
