from datetime import date

from sqlalchemy import event, select, and_

from zimaApp.dao.base import BaseDAO
from zimaApp.database import async_session_maker

from zimaApp.wells_data.models import WellsData
from zimaApp.wells_repair_data.models import WellsRepair
from zimaApp.norms.models import NormsWork


class WellsDatasDAO(BaseDAO):
    model = WellsData

    @staticmethod
    async def find_wells_with_repairs_and_norms(
            well_number: str,
            contractor_id: int
    ):
        async with async_session_maker() as session:
            """
            Извлекает скважины, их ремонты и связанные нормы одним JOIN-запросом.
            """
            query = select(
                WellsData.well_number,
                WellsData.well_area,
                WellsRepair.type_kr,
                WellsRepair.work_plan,
                NormsWork.date_create,
                NormsWork.id
            ).join(
                WellsRepair, WellsData.id == WellsRepair.wells_id  # JOIN WellsDatas с WellsRepairs
            ).join(
                NormsWork, WellsRepair.id == NormsWork.repair_id  # JOIN WellsRepairs с Norm
            ).where(
                and_(
                    WellsData.well_number == well_number,
                    WellsData.contractor == contractor_id
                )
            )

            result = await session.execute(query)
            return result.all()

    @staticmethod
    async def find_wells_with_repairs(
            well_number: str,
            contractor_id: int
    ):
        async with async_session_maker() as session:
            """
            Извлекает скважины, их ремонты и связанные нормы одним JOIN-запросом.
            """
            query = select(
                WellsData.well_number,
                WellsData.well_area,
                WellsRepair.type_kr,
                WellsRepair.work_plan,
                WellsRepair.date_create,
                WellsData.id
            ).join(
                WellsRepair, WellsData.id == WellsRepair.wells_id  # JOIN WellsDatas с WellsRepairs
            ).where(
                and_(
                    WellsData.well_number == well_number,
                    WellsData.contractor == contractor_id
                )
            )

            result = await session.execute(query)
            return result.all()

    @staticmethod
    async def find_wells_with_repairs_one_or_none(
            well_number: str,
            well_area: str,
            type_kr: str,
            date_create: date,
            work_plan: str,
            contractor: str,
    ):
        async with async_session_maker() as session:
            query = select(
                WellsRepair.id,
                WellsData.well_number,
                WellsData.well_area,
                WellsRepair.category_dict,
                WellsRepair.type_kr,
                WellsRepair.work_plan,
                WellsRepair.excel_json,
                WellsRepair.data_change_paragraph,
                WellsRepair.perforation_project,
                WellsRepair.type_absorbent,
                WellsRepair.static_level,
                WellsRepair.dinamic_level,
                WellsRepair.expected_data,
                WellsRepair.curator,
                WellsRepair.region
                ).join(WellsRepair, WellsData.id == WellsRepair.wells_id).where(
                and_(WellsData.well_number == well_number,
                     WellsData.well_area == well_area,
                     WellsRepair.type_kr == type_kr,
                     WellsRepair.work_plan == work_plan,
                     WellsRepair.date_create == date_create,
                     WellsRepair.contractor == contractor))
            result = await session.execute(query)
            return result.mappings().first()
