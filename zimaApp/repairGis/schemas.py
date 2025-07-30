from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional

from pydantic import BaseModel

class RepairGisUpdate(BaseModel):
    id: int
    fields: Dict[str, Any]

class ColumnEnum(str, Enum):
    well_number="well_number"
    well_area="well_area"
    status="status"
    contractor_gis="contractor_gis"
    downtime_start="downtime_start"

class SRepairsGis(BaseModel):
    well_id: int
    contractor_gis: str
    message_time: datetime
    downtime_start: datetime | None
    downtime_end: datetime | None
    downtime_duration: int | float | None
    downtime_reason: str
    work_goal: str
    contractor_opinion: str | None
    downtime_duration_meeting_result: float | None
    meeting_result: str | None
    image_pdf: str | None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


# Модель для ответа
class RepairGisResponse(BaseModel):
    id: int
    well_number: str  # номер скважины
    well_area: str  # площадь скважины
    status: str
    contractor_gis: str
    message_time: Optional[datetime]
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