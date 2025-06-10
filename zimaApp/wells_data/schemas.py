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
    well_number: str
    well_area: str
    well_oilfield: str
    cdng: str
    costumer: Optional[str]
    inventory_number: Optional[str]
    wellhead_fittings: Optional[str]
    appointment: Optional[str]
    angle_data: Optional[Dict]
    column_direction: Optional[Dict]
    column_conductor: Optional[Dict]
    column_production: Optional[Dict]
    column_additional: Optional[Dict]
    bottom_hole_drill: Optional[Union[float, int]] = None
    bottom_hole_artificial: Optional[Union[float, int]] = None
    max_angle: Optional[Union[float, int]] = None
    distance_from_rotor_table: Optional[Union[float, int]] = None
    max_angle_depth: Optional[Union[float, int]] = None
    max_expected_pressure: Optional[Union[float, int]] = None
    max_admissible_pressure: Optional[Union[float, int]] = None
    rotor_altitude: Optional[Union[float, int]] = None
    perforation: Optional[Dict]
    equipment: Optional[Dict]
    nkt_data: Optional[Dict]
    sucker_pod: Optional[Dict]
    diameter_doloto_ek: Optional[Union[float, int]] = None
    last_pressure_date: Optional[date]
    date_commissioning: Optional[date]
    date_drilling_run: Optional[date]
    date_drilling_finish: Optional[date]
    geolog: Optional[str]
    date_create: Optional[date]
    leakiness: Optional[Dict]
    contractor: Optional[str]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

    @property
    def column_direction(self) -> Optional[ColumnDirection]:
        if self._column_direction:
            return ColumnDirection.model_validate(self._column_direction)
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
            return ColumnConductor.model_validate(self._column_conductor)
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
            return ColumnProduction.model_validate(self._column_production)
        return None

    @column_production.setter
    def column_production(self, value: Optional[ColumnProduction]):
        if value:
            self._column_production = value.dict()
        else:
            self._column_production = False
