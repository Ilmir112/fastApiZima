from datetime import datetime

from pydantic import BaseModel


class SRepairTime(BaseModel):
    brigade_id: int
    well_id: int
    brigade_summary_id: int
    start_time: datetime
    end_time: datetime | None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class SRepairTimeClose(BaseModel):
    brigade_summary_id: int
    end_time: str
