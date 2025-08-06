from enum import Enum

from sqlalchemy import JSON, Column, Date, Integer, String, ForeignKey, Float, Text, DateTime
from sqlalchemy.orm import relationship
from typing import Optional

from zimaApp.database import Base

from zimaApp.wells_repair_data.models import StatusWorkPlan

class StatusSummary(str, Enum):
    OPEN = "открыт"
    ClOSE = "закрыт"
    PAUSE = "приостановлен"

class RepairTime(Base):
    __tablename__ = 'repair_times'

    id = Column(Integer, primary_key=True)
    brigade_id = Column(Integer, ForeignKey('brigades.id'), nullable=False)
    well_id = Column(Integer, ForeignKey('wells.id'), nullable=True)
    status = Column(Enum(StatusSummary), default=StatusSummary.OPEN, nullable=False)
    brigade_summary_id = Column(Integer, ForeignKey('brigade_summary.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
