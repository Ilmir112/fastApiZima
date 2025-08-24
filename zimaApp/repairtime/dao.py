from typing import Optional, Union, List

from sqlalchemy import select, join
from sqlalchemy.orm import selectinload, joinedload

from zimaApp.brigade.models import Brigade
from zimaApp.dao.base import BaseDAO
from zimaApp.database import async_session_maker
from zimaApp.logger import logger
from zimaApp.repairtime.models import RepairTime, StatusSummary
from zimaApp.summary.models import BrigadeSummary
from zimaApp.wells_data.models import WellsData


class RepairTimeDAO(BaseDAO):
    model = RepairTime

    @classmethod
    async def find_by_well_number(cls, well_number: str):
        async with async_session_maker() as session:
            query = (
                select(RepairTime)
                .join(RepairTime.well)
                .filter(WellsData.well_number == well_number)
                .options(
                    joinedload(RepairTime.well),
                    joinedload(RepairTime.brigade),
                    joinedload(RepairTime.brigade_summary)
                )
            )
            result = await session.execute(query)
            return result.scalars().unique().all()

    @classmethod
    async def get_all(
            cls,
            status: Optional[Union[StatusSummary, List[StatusSummary]]] = None
    ):
        async with async_session_maker() as session:
            try:
                query = (
                    select(cls.model)
                    .options(
                        selectinload(cls.model.brigade),
                        selectinload(cls.model.well)
                    )
                )

                # Обработка фильтрации по статусу
                if status is not None:
                    if isinstance(status, list):
                        query = query.where(cls.model.status.in_(status))
                    else:
                        query = query.where(cls.model.status == status)

                result = await session.execute(query)
                repair_times = result.scalars().all()
                return repair_times

            except Exception as e:
                # Предполагается наличие логгера
                logger.error(f"Error in get_all: {e}")
                return []


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
                        video_path=brigade_data.get("video_path"),

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
