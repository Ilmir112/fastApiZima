from typing import Optional, List

from fastapi.params import Depends
from pydantic import BaseModel

from zimaApp.repairtime.schemas import SRepairTime
from zimaApp.summary.models import TimeWorkEnum
from zimaApp.wells_repair_data.models import StatusWorkPlan
from datetime import date, datetime


class SBrigadeSummary(BaseModel):
    date_summary: date
    time_interval: TimeWorkEnum
    work_details: str
    notes: str | None
    act_path: str | None
    status_act: StatusWorkPlan
    photo_path: list | None
    video_path: list | None

    repair_times: SRepairTime


    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

# Модель для входных данных
class DeletePhotoRequest(BaseModel):
    itemId: int


class SUpdateSummary(BaseModel):
    date_summary: datetime
    work_details: str

    class Config:
        # Включить поддержку timezone-aware datetime
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }



