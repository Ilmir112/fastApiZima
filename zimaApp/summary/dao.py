from sqlalchemy import select
from sqlalchemy.orm import selectinload

from zimaApp.dao.base import BaseDAO
from zimaApp.database import async_session_maker
from zimaApp.logger import logger
from zimaApp.repairtime.models import StatusSummary, RepairTime
from zimaApp.summary.models import BrigadeSummary


class BrigadeSummaryDAO(BaseDAO):
    model = BrigadeSummary


    @classmethod
    async def get_summary_list(cls,**filter_by):
        try:
            async with async_session_maker() as session:
                query = (
                    select(
                        cls.model.date_summary,
                        cls.model.time_interval,
                        cls.model.work_details,
                        cls.model.notes
                    )
                    .filter_by(**filter_by)
                    .order_by(cls.model.date_summary)
                )

                result = await session.execute(query)
                # Получаем список строк (кортежей)
                records = result.all()
                new_list = []
                for date_summary, time_interval, work_details, notes in records:
                    new_list.append((f'{date_summary.strftime("%d.%m.%Y")}\n{time_interval.value}',
                                     work_details, notes))

                return sorted(new_list, key=lambda x: BrigadeSummaryDAO.extract_date(x[0]))
        except Exception as e:
            logger.error(f"Error fetching summary list: {e}")
            return []


