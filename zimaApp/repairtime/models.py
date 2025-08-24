from enum import Enum as enum

from sqlalchemy import JSON, Column, Date, Integer, String, ForeignKey, Float, Text, DateTime, Enum, TIMESTAMP
from sqlalchemy.orm import relationship
from typing import Optional

from zimaApp.database import Base

from zimaApp.wells_repair_data.models import StatusWorkPlan

class StatusSummary(str, enum):
    OPEN = "открыт"
    ClOSE = "закрыт"
    PAUSE = "приостановлен"

class RepairTime(Base):
    __tablename__ = "repair_times"

    id = Column(Integer, primary_key=True)
    brigade_id = Column(Integer, ForeignKey('brigade.id'), nullable=False)
    well_id = Column(Integer, ForeignKey('wells_data.id'), nullable=True)
    wells_repair_id = Column(Integer, ForeignKey('wells_repairs.id'), nullable=True)
    status = Column(Enum(StatusSummary), default=StatusSummary.OPEN, nullable=False)
    # brigade_summary_id = Column(Integer, ForeignKey('brigade_summary.id'), nullable=False)
    start_time = Column(TIMESTAMP(timezone=True), nullable=False)
    end_time = Column(TIMESTAMP(timezone=True), nullable=True)
    duration_repair = Column(Float, nullable=True)
    norms_work = Column(JSON, nullable=True)
    norms_time = Column(Float, nullable=True)

    brigade = relationship("Brigade", back_populates="repair_times")
    well = relationship("WellsData", back_populates="repair_times")
    wells_repair = relationship("WellsRepair", back_populates="repair_times")

    brigade_summary = relationship(
        "BrigadeSummary",
        back_populates="repair_time",
        uselist=False,
        cascade="all, delete-orphan"
    )