from enum import Enum

from sqlalchemy import JSON, Column, Date, Integer, String, ForeignKey, Float, Text, DateTime
from sqlalchemy.orm import relationship
from typing import Optional

from zimaApp.database import Base
from zimaApp.wells_repair_data.models import StatusWorkPlan


class TimeWorkEnum(str, Enum):
    ONE = "02:00-06:00"
    TWO = "06:00-14:00"
    THREE = "14:00-18:00"
    FOUR = "18:00-22:00"
    FIVE = "22:00-02:00"




class BrigadeSummary(Base):
    __tablename__ = 'brigade_summary'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    time_interval = Column(TimeWorkEnum, nullable=False)
    work_details = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    act_path = Column(Text, default=None, nullable=True)
    status_act = Column(Enum(StatusWorkPlan), default=StatusWorkPlan.NOT_SIGNED, nullable=True)
    foto_path = Column(Text, default=None, nullable=True)
    video_path = Column(Text, default=None, nullable=True)

    repair_times = relationship("RepairTime", backref="brigade_summary")
