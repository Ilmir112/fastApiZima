from datetime import date
from pydantic import BaseModel
import json


class SWellsRepair(BaseModel):
    id: int
    well_number: str
    area_well: str
    well_oilfield: str
    cdng: str
    type_kr: json
    work_plan: str
    contractor: str
    geolog: str
    date_create: date
    data_well: json
    costumer: str
    excel_json: json
    data_change_paragraph: json
    category_dict: json
    appointment: str
    inventory_number: str
    wellhead_fittings: str
    angle_data: json

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

