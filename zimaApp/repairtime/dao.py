from sqlalchemy import select
from sqlalchemy.orm import selectinload

from zimaApp.dao.base import BaseDAO
from zimaApp.database import async_session_maker
from zimaApp.logger import logger
from zimaApp.repairtime.models import RepairTime
from zimaApp.summary.models import BrigadeSummary


class RepairTimeDAO(BaseDAO):
    model = RepairTime

    @classmethod
    async def add_brigade_with_repairs(cls, brigade_data: dict, rt_data: dict):
        try:
            async with async_session_maker() as session:
                try:
                    # Создаем объект BrigadeSummary
                    repairs_obj = cls.model(**rt_data)
                    session.add(repairs_obj)
                    await session.flush()  # чтобы получить id

                    summary_data = BrigadeSummary(
                        date_summary=brigade_data.get("date_summary"),
                        time_interval=brigade_data.get("time_interval"),
                        work_details=brigade_data.get("work_details"),
                        repair_time_id=repairs_obj.id,
                        notes=brigade_data.get("notes"),
                        act_path=brigade_data.get("act_path"),
                        status_act=brigade_data.get("status_act"),
                        photo_path=brigade_data.get("photo_path"),
                        video_path=brigade_data.get("video_path")
                    )
                    session.add(summary_data)

                    # Коммитим все вместе
                    await session.commit()
                    return repairs_obj

                except Exception as e:
                    await session.rollback()
                    logger.error(f"Ошибка при добавлении данных: {e}", exc_info=True)
                    raise
        except Exception as e:
            logger.error(f"Ошибка в add_brigade_with_repairs: {e}", exc_info=True)
            raise

    @classmethod
    async def find_by_id_repair(cls, summary_id):
        async with async_session_maker() as session:
            result = await session.execute(
                select(RepairTime).options(selectinload(RepairTime.brigade_summary)).where(
                    RepairTime.id == summary_id)
            )
            return result.scalar_one_or_none()
