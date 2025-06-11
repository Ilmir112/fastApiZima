import json
from datetime import date, datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel


class TypeTKRS(str, Enum):
    KRS = "КРС"
    TRS = "ТРС"


class SNorms(BaseModel):
    repair_id: int
    start_well_repair: datetime
    repair_well_repair: Optional[datetime] = None
    type_tkrs: TypeTKRS
    summary_work: dict
    norms_json: dict
    lifting_unit: str
    number_brigade: str
    norms_time: float


    class Config:
        from_attributes = True
        arbitrary_types_allowed = True