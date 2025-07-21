from datetime import datetime, timedelta

from pydantic import BaseModel


class SRepairsGis(BaseModel):
    contractor_gis: str
    message_time: datetime
    downtime_start: datetime
    downtime_end: datetime
    downtime_duration: float
    downtime_reason: str
    work_goal: str
    contractor_opinion: str
    downtime_duration_meeting_result: float
    meeting_result: str
    image_pdf: str

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


