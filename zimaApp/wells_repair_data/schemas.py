import json
from datetime import date
from typing import Literal

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
    perforation_project: dict
    type_absorbent: str # Literal["EVASORB марки 121", "ХИМТЕХНО 101 Марка А", "СНПХ-1200", "ПСВ-3401", "Гастрит-К131М"]
    static_level: float
    dinamic_level: float
    expected_data: dict
    curator: str
    region: str

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class SNewWellDatas(BaseModel):
    wells_id: int