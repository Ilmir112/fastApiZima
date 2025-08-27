from pydantic import BaseModel
from datetime import datetime

class RepairDataCreate(BaseModel):
    contractor: str
    brigade_number: str
    well_area: str
    well_number: str
    begin_time: datetime
    finish_time: datetime | None
    duration_repair: float | None
    category_repair: str | None
    repair_code: str
    type_repair: str | None
    bush: str

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class SRepairGet(BaseModel):
    well_area: str
    well_number: str
    begin_time: datetime