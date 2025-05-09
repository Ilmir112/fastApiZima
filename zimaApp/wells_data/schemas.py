from typing import Dict, Any, Literal, Optional, Union
from datetime import date

from pydantic import BaseModel, confloat, constr


class ColumnInfo(BaseModel):
    diameter: Optional[confloat(ge=70, le=500)]
    wall_thickness: confloat(ge=4, le=16)
    head: float
    shoe: float
    level_cement: float


class ColumnDirection(ColumnInfo):
    pass


class ColumnConductor(ColumnInfo):
    pass


class ColumnAdditional(ColumnInfo):
    diameter: Optional[confloat(ge=70, le=170)]
    wall_thickness: confloat(ge=4, le=16)


class ColumnProduction(ColumnInfo):
    diameter: Optional[confloat(ge=70, le=211)]
    pass


class SWellsData(BaseModel):
    id: int
    well_number: constr(min_length=1, max_length=10)
    area_well: constr(min_length=1, max_length=50)
    well_oilfield: constr(min_length=1, max_length=50)
    costumer: str
    cdng: str
    inventory_number: str
    wellhead_fittings: str
    appointment: str
    angle_data: Dict[str, Any]
    column_direction: Union[False, ColumnDirection]
    column_conductor: Union[False, ColumnConductor]
    column_production: Union[False, ColumnProduction]
    column_additional: Union[False, ColumnAdditional]
    bottom_hole_drill: Optional[confloat(ge=10, le=7000)]
    bottom_hole_artificial: Optional[confloat(ge=10, le=7000)]
    max_angle: Optional[confloat(ge=0, le=102)]
    distance_from_rotor_table: Optional[confloat(ge=0, le=12)]
    max_angle_depth: float
    max_expected_pressure: Optional[confloat(ge=10, le=151)]
    max_admissible_pressure: Optional[confloat(ge=10, le=151)]
    rotor_altitude: float
    perforation: Dict[str, Any]
    equipment: Dict[str, Any]
    nkt_data: Dict[str, Any]
    sucker_pod: Dict[str, Any]
    diameter_doloto_ek: float
    last_pressure_date: date
    date_commissioning: date
    date_drilling_run: date
    date_drilling_finish: date

    geolog: str
    date_create: date

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


    @property
    def column_direction(self) -> Optional[ColumnDirection]:
        if self._column_direction:
            return ColumnDirection.parse_obj(self._column_direction)
        return None

    @column_direction.setter
    def column_direction(self, value: Optional[ColumnDirection]):
        if value:
            self._column_direction = value.dict()
        else:
            self._column_direction = False

    @property
    def column_conductor(self) -> Optional[ColumnConductor]:
        if self._column_conductor:
            return ColumnConductor.parse_obj(self._column_conductor)
        return None

    @column_conductor.setter
    def column_conductor(self, value: Optional[ColumnConductor]):
        if value:
            self._column_conductor = value.dict()
        else:
            self._column_conductor = False

    @property
    def column_production(self) -> Optional[ColumnProduction]:
        if self._column_production:
            return ColumnProduction.parse_obj(self._column_production)
        return None

    @column_production.setter
    def column_production(self, value: Optional[ColumnProduction]):
        if value:
            self._column_production = value.dict()
        else:
            self._column_production = False








