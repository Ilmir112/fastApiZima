from datetime import datetime, timedelta

from pydantic import BaseModel


class SRepairsGis(BaseModel):
    well_id: int
    contractor_gis: str
    message_time: datetime
    downtime_start: datetime | None
    downtime_end: datetime | None
    downtime_duration: float | None
    downtime_reason: str
    work_goal: str
    contractor_opinion: str | None
    downtime_duration_meeting_result: float | None
    meeting_result: str | None
    image_pdf: str | None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


