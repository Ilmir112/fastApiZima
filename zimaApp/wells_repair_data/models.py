from sqlalchemy import JSON, Column, Date, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from typing import Optional

from zimaApp.database import Base


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
    geolog_id = Column(Integer, ForeignKey('users.id'))
    date_create: Date = Column(Date, nullable=False)
