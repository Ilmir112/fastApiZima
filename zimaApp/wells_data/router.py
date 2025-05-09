from fastapi import APIRouter, Depends

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
async def find_wells_in_silencing_for_region(wells_data: WellsSearchArgs = Depends()):
    result = await WellsDatasDAO.find_one_or_none(
        well_number=wells_data.well_number, deposit_area=wells_data.well_area
    )
    return result


@router.post("/add_wells_data")
@version(1)
async def add_wells_data(well_data: SWellsData):
    print
    wells = WellsDatasDAO.add_data(
        well_number=well_data.well_number,
        area_well=well_data.area_well,
        well_oilfield=well_data.well_oilfield,
        cdng=well_data.cdng,
        costumer=well_data.costumer,
        inventory_number=well_data.inventory_number,
        wellhead_fittings=well_data.wellhead_fittings,
        appointment=well_data.appointment,
        angle_data=well_data.angle_data,
        column_direction=well_data.column_direction.dict(),
        column_conductor=well_data.column_conductor.dict(),

        column_production=well_data.column_production.dict(),
        column_additional=well_data.column_additional.dict(),
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
        geolog=well_data.geolog,
        date_create=well_data.date_create
    )
    await wells