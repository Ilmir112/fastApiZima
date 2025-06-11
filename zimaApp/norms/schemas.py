import json
from datetime import date, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel


class TypeTKRS(str, Enum):
    KRS = "КРС"
    TRS = "ТРС"


class SNorms(BaseModel):
    id: int
    repair_id: int
    start_well_repair: datetime
    repair_well_repair: datetime
    type_tkrs: TypeTKRS
    summary_work: dict
    norms_json: dict
    creater_id: int
    lifting_unit: str
    number_brigade: str
    norms_time: float

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True