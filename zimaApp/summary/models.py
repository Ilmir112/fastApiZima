from enum import Enum as enum

from sqlalchemy import JSON, Column, Date, Integer, String, ForeignKey, Float, Text, DateTime, Enum as SqlEnum, ARRAY, \
    UniqueConstraint
from sqlalchemy.orm import relationship
from typing import Optional, List

from zimaApp.database import Base
from zimaApp.wells_repair_data.models import StatusWorkPlan


class TimeWorkEnum(str, enum):
    EARLY_MORNING = "02:00-06:00"
    MORNING = "06:00-10:00"
    LATE_MORNING = "10:00-14:00"
    AFTERNOON = "14:00-18:00"
    EVENING = "18:00-22:00"
    NIGHT = "22:00-02:00"

status_enum = SqlEnum(
    StatusWorkPlan,
    name='statusworkplan2',
    native_enum=True,
    create_type=False  # или True, если хотите создать автоматически
)


class BrigadeSummary(Base):
    __tablename__ = 'brigade_summary'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_summary = Column(Date, nullable=False)
    time_interval = Column(SqlEnum(TimeWorkEnum), nullable=False)
    work_details = Column(Text, nullable=False)
    repair_time_id = Column(Integer, ForeignKey('repair_times.id', ondelete='CASCADE'), nullable=False)
    notes = Column(Text, nullable=True)
    act_path = Column(ARRAY(String), default=None, nullable=True)
    status_act = Column(status_enum, default=StatusWorkPlan.NOT_SIGNED.value, nullable=True)
    photo_path = Column(ARRAY(String), default=None, nullable=True)
    video_path = Column(ARRAY(String), default=None, nullable=True)

    # Добавьте это свойство
    repair_time = relationship(
        "RepairTime",
        back_populates="brigade_summary"
    )


    __table_args__ = (
        UniqueConstraint('date_summary', 'time_interval', 'repair_time_id', name='uix_date_time'),
    )
