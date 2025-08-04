from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.testing.suite.test_reflection import users

from zimaApp.logger import logger
from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users
from zimaApp.well_silencing.router import WellsSearchArgs
from zimaApp.wells_data.dao import WellsDatasDAO
from zimaApp.wells_data.models import WellsData
from zimaApp.wells_data.schemas import SWellsData
from fastapi_versioning import version

router = APIRouter(
    prefix="/wells_data_router",
    tags=["Данные по скважинам"],
)


@router.get("/find_wells_data")
@version(1)
# @cache(expire=60)
async def find_wells_data(wells_data: WellsSearchArgs = Depends()):
    try:
        result = await WellsDatasDAO.find_one_or_none(
            well_number=wells_data.well_number, well_area=wells_data.well_area
        )
    except SQLAlchemyError as e:
        logger.error(e)
    return result


@router.get("/find_wells_data_by_id")
@version(1)
# @cache(expire=60)
async def find_wells_data_by_id(wells_id: int):
    result = await WellsDatasDAO.find_one_or_none(id=wells_id)
    return result


@router.post("/add_wells_data")
@version(1)
async def add_wells_data(
    well_data: SWellsData, user: Users = Depends(get_current_user)
):
    try:
        result = await WellsDatasDAO.find_one_or_none(
            well_number=well_data.well_number, well_area=well_data.well_area
        )
        if result is None:
            result = await WellsDatasDAO.add_data(
                well_number=well_data.well_number,
                well_area=well_data.well_area,
                well_oilfield=well_data.well_oilfield,
                cdng=well_data.cdng,
                costumer=well_data.costumer,
                inventory_number=well_data.inventory_number,
                wellhead_fittings=well_data.wellhead_fittings,
                appointment=well_data.appointment,
                angle_data=well_data.angle_data,
                column_direction=well_data.column_direction,
                column_conductor=well_data.column_conductor,
                column_production=well_data.column_production,
                column_additional=well_data.column_additional,
                bottom_hole_drill=well_data.bottom_hole_drill,
                bottom_hole_artificial=well_data.bottom_hole_artificial,
                max_angle=well_data.max_angle,
                distance_from_rotor_table=well_data.distance_from_rotor_table,
                max_angle_depth=well_data.max_angle_depth,
                max_expected_pressure=well_data.max_expected_pressure,
                max_admissible_pressure=well_data.max_admissible_pressure,
                rotor_altitude=well_data.rotor_altitude,
                perforation=well_data.perforation,
                equipment=well_data.equipment,
                nkt_data=well_data.nkt_data,
                sucker_pod=well_data.sucker_pod,
                diameter_doloto_ek=well_data.diameter_doloto_ek,
                last_pressure_date=well_data.last_pressure_date,
                date_commissioning=well_data.date_commissioning,
                date_drilling_run=well_data.date_drilling_run,
                date_drilling_finish=well_data.date_drilling_finish,
                leakiness=well_data.leakiness,
                geolog=user.login_user,
                date_create=well_data.date_create,
                contractor=well_data.contractor,
            )
            return result
    except SQLAlchemyError as db_err:
        msg = f"Database Exception {db_err}"
        logger.error(
            msg,
            extra={
                "well_number": well_data.well_number,
                "well_area": well_data.well_area,
            },
            exc_info=True,
        )
    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(
            msg,
            extra={
                "well_number": well_data.well_number,
                "well_area": well_data.well_area,
            },
            exc_info=True,
        )


@router.put("/update_wells_data")
@version(1)
async def update_wells_data(
    new_well_data: SWellsData,
    well_data: SWellsData = Depends(find_wells_data),
    user: Users = Depends(get_current_user),
):
    try:
        result = await WellsDatasDAO.update_data(
            well_data.id,
            well_number=new_well_data.well_number,
            well_area=new_well_data.well_area,
            well_oilfield=new_well_data.well_oilfield,
            cdng=new_well_data.cdng,
            costumer=new_well_data.costumer,
            inventory_number=new_well_data.inventory_number,
            wellhead_fittings=new_well_data.wellhead_fittings,
            appointment=new_well_data.appointment,
            angle_data=new_well_data.angle_data,
            column_direction=new_well_data.column_direction,
            column_conductor=new_well_data.column_conductor,
            column_production=new_well_data.column_production,
            column_additional=new_well_data.column_additional,
            bottom_hole_drill=new_well_data.bottom_hole_drill,
            bottom_hole_artificial=new_well_data.bottom_hole_artificial,
            max_angle=new_well_data.max_angle,
            distance_from_rotor_table=new_well_data.distance_from_rotor_table,
            max_angle_depth=new_well_data.max_angle_depth,
            max_expected_pressure=new_well_data.max_expected_pressure,
            max_admissible_pressure=new_well_data.max_admissible_pressure,
            rotor_altitude=new_well_data.rotor_altitude,
            perforation=new_well_data.perforation,
            equipment=new_well_data.equipment,
            nkt_data=new_well_data.nkt_data,
            sucker_pod=new_well_data.sucker_pod,
            diameter_doloto_ek=new_well_data.diameter_doloto_ek,
            last_pressure_date=new_well_data.last_pressure_date,
            date_commissioning=new_well_data.date_commissioning,
            date_drilling_run=new_well_data.date_drilling_run,
            date_drilling_finish=new_well_data.date_drilling_finish,
            leakiness=new_well_data.leakiness,
            geolog=user.login_user,
            date_create=new_well_data.date_create,
            contractor=new_well_data.contractor,
        )
        logger.info(
            "wells update",
            extra={
                "well_number": well_data.well_number,
                "well_area": well_data.well_area,
            },
            exc_info=True,
        )
        return result

    except (SQLAlchemyError, Exception) as e:
        msg = f"Unexpected error: {str(e)}"

        logger.error(
            msg,
            extra={
                "well_number": well_data.well_number,
                "well_area": well_data.well_area,
            },
            exc_info=True,
        )


@router.delete("/delete_wells_data")
@version(1)
async def delete_wells_data(
    well_data: WellsSearchArgs = Depends(find_wells_data),
    user: Users = Depends(get_current_user),
):
    try:

        result = await WellsDatasDAO.delete_item_all_by_filter(
            well_number=well_data.well_number, well_area=well_data.well_area
        )
        logger.info(
            "wells delete",
            extra={
                "well_number": well_data.well_number,
                "well_area": well_data.well_area,
            },
            exc_info=True,
        )
        return {"status": "success", "id": result}

    except (SQLAlchemyError, Exception) as e:
        msg = f"Unexpected error: {str(e)}"

        logger.error(
            msg,
            extra={
                "well_number": well_data.well_number,
                "well_area": well_data.well_area,
            },
            exc_info=True,
        )
