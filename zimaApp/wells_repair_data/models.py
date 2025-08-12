from enum import Enum

from pygments.lexer import default
from sqlalchemy import JSON, Column, Date, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from typing import Optional
from sqlalchemy import Enum as SqlEnum

from zimaApp.database import Base


class StatusWorkPlan(str, Enum):
    NOT_SIGNED = "не подписан"
    PLAN_IS_SIGNED = "подписан"
    FULLY_NOT_SIGNED = "подписан не полностью"


class WellsRepair(Base):
    __tablename__ = "wells_repairs"

    id: int = Column(Integer, primary_key=True)
    wells_id: int = Column(Integer, ForeignKey("wells_data.id"))
    category_dict: dict = Column(JSON, nullable=False)
    type_kr: str = Column(String, nullable=False)
    work_plan: str = Column(String, nullable=False)
    excel_json: dict = Column(JSON, nullable=False)
    data_change_paragraph: dict = Column(JSON, nullable=False)
    norms_time: float = Column(Float, nullable=False)
    chemistry_need: dict = Column(JSON, nullable=False)
    geolog_id = Column(Integer, ForeignKey("users.id"))
    date_create: Date = Column(Date, nullable=False)
    perforation_project: dict = Column(JSON)
    type_absorbent: str = Column(String)
    static_level: float = Column(Float, nullable=True)
    dinamic_level: float = Column(Float, nullable=True)
    expected_data: dict = Column(JSON, nullable=False)
    curator: str = Column(String, nullable=False)
    region: str = Column(String, nullable=False)
    contractor: str = Column(String, nullable=False)
    signed_work_plan_path: str = Column(String, nullable=True)
    status_work_plan: StatusWorkPlan = Column(
        SqlEnum(StatusWorkPlan, native_enum=True,
                create_type=False), default=StatusWorkPlan.NOT_SIGNED.value, nullable=True
    )

    well_data = relationship("WellsData", back_populates="repairs")
    users = relationship("Users", back_populates="wells_repairs")
    norms = relationship("NormsWork", back_populates="well_repair")
