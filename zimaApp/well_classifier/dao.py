from typing import List, Optional

from sqlalchemy import select

from zimaApp.dao.base import BaseDAO
from zimaApp.database import async_session_maker
from zimaApp.well_classifier.models import WellClassifier


class WellClassifierDAO(BaseDAO):
    model = WellClassifier

    @classmethod
    async def get_unique_well_area(cls) -> List[Optional[str]]:
        async with async_session_maker() as session:
            result = await session.execute(select(WellClassifier.well_area).distinct())
            return result.scalars().all()
