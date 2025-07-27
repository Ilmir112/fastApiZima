from enum import Enum

from sqlalchemy import JSON, Column, Date, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from typing import Optional

from zimaApp.database import Base


class StatusEnum(str, Enum):
    OPEN = 'открыт'
    CLOSE = "закрыт"
    DELETE = 'без простоя'


class RepairsGis(Base):
    __tablename__ = "repair_gis"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(Integer, ForeignKey('wells_data.id'), nullable=False)
    status = Column(String, default=StatusEnum.OPEN, nullable=False)
    contractor_gis = Column(String, nullable=False)
    message_time = Column(DateTime(timezone=True), nullable=False)
    downtime_start = Column(DateTime(timezone=True), nullable=True)  # начало простоя
    downtime_end = Column(DateTime(timezone=True), nullable=True)  # окончание простоя
    downtime_duration = Column(Float, nullable=True)  # время простоя (в часах или минутах)
    downtime_reason = Column(String, nullable=True)  # причина простоя
    work_goal = Column(String, nullable=True)  # цель работ
    contractor_opinion = Column(String, nullable=True)  # мнение подрядчика
    downtime_duration_meeting_result = Column(Float, nullable=True)
    meeting_result = Column(String, nullable=True)  # результат совещания
    image_pdf = Column(String, nullable=True)

    # Связь с WellsData
    well = relationship("WellsData", back_populates="repairs_gis")