import json
from datetime import date

from pydantic import BaseModel


class SWellsRepair(BaseModel):
    id: int
    category_dict: dict
    type_kr: str
    work_plan: str
    excel_json: dict
    data_change_paragraph: dict
    norms_time: float
    chemistry_need: dict
    geolog_id: str
    date_create: date

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class SNewWellDatas(BaseModel):
    wells_id: int