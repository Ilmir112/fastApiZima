from datetime import datetime, timedelta

from typing import Optional, Union, List

from sqlalchemy import select, join, or_, and_
from sqlalchemy.orm import selectinload, joinedload

from zimaApp.brigade.models import Brigade
from zimaApp.dao.base import BaseDAO
from zimaApp.database import async_session_maker
from zimaApp.logger import logger
from zimaApp.repairtime.models import RepairTime, StatusSummary
from zimaApp.summary.models import BrigadeSummary
from zimaApp.wells_data.models import WellsData
from zimaApp.wells_repair_data.models import WellsRepair


class RepairTimeDAO(BaseDAO):
    model = RepairTime

    @classmethod
    async def get_type_kr(cls,
                          repair_time_id: int
                          ):
        try:
            async with async_session_maker() as session:
                query = (
                    select(RepairTime)
                    .filter(RepairTime.id == repair_time_id).options(
                    joinedload(RepairTime.wells_repair)
                )
                )
                result = await session.execute(query)
                # Получаем все значения
                values = result.scalar_one_or_none()
                # Возвращаем уникальные значения
                return values.wells_repair
        except Exception as e:
            # Предполагается наличие логгера
            logger.error(f"Error in get_all: {e}")
            return

    @classmethod
    async def check_brigade_and_well_availability(
            cls,
            brigade_id: int,
            well_id: int,
            start_time: datetime,
            end_time: datetime = None
    ):
        """
        Проверяет, занята ли бригада или скважина в интервале [start_time, end_time].
        Если end_time не указано, ищем все ремонты, пересекающиеся с этим интервалом.
        Возвращает True, если занято (есть пересечения), иначе False.
        """

        # Если end_time не указано, считаем текущим временем
        if end_time is None:
            end_time = datetime.utcnow()

        async with async_session_maker() as session:
            # Проверка занятости бригады
            brigade_conflict = await session.execute(
                select(RepairTime).where(
                    and_(
                        RepairTime.brigade_id == brigade_id,
                        RepairTime.start_time < end_time,
                        or_(
                            RepairTime.end_time == None,
                            RepairTime.end_time > start_time
                        )
                    )
                )
            )
            brigade_conflict_exists = brigade_conflict.scalars().first() is not None

            # Проверка занятости скважины другой бригадой
            well_conflict = await session.execute(
                select(RepairTime).where(
                    and_(
                        RepairTime.well_id == well_id,
                        RepairTime.brigade_id != brigade_id,
                        RepairTime.start_time < end_time,
                        or_(
                            RepairTime.end_time == None,
                            RepairTime.end_time > start_time
                        )
                    )
                )
            )
            well_conflict_exists = well_conflict.scalars().first() is not None

            return brigade_conflict_exists or well_conflict_exists

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
                    joinedload(RepairTime.brigade_summary),
                    # joinedload(RepairTime.wells_repair)
                )
            )
            result = await session.execute(query)
            return result.scalars().unique().all()

    @classmethod
    async def find_repair_params_by_id(cls, repair_id: int):
        async with async_session_maker() as session:
            query = (
                select(RepairTime)
                .join(RepairTime.well)
                .filter(RepairTime.id == repair_id)
                .options(
                    joinedload(RepairTime.well),
                    joinedload(RepairTime.brigade),
                    joinedload(RepairTime.brigade_summary)
                )
            )
            result = await session.execute(query)
            return result.scalars().first()

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
