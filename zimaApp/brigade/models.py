from sqlalchemy import JSON, Column, Date, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from typing import Optional

from zimaApp.database import Base


class Brigade(Base):
    __tablename__ = 'brigade'

    id = Column(Integer, primary_key=True)
    contractor = Column(String, nullable=False)
    costumer = Column(String, nullable=False)
    expedition = Column(String, nullable=False)
    number_brigade = Column(Integer, nullable=False, unique=True)
    brigade_master = Column(JSON, nullable=False)
    phone_number_brigade = Column(String, nullable=False)
    lifting_unit = Column(String, nullable=False)
    hydraulic_wrench = Column(String, nullable=False)
    weight_indicator = Column(String, nullable=False)
    brigade_composition = Column(JSON)
    pvo_type = Column(String, nullable=False)
    number_pvo = Column(Integer, nullable=False)
#
#
# class Brigade(Base):
#     __tablename__ = "brigade"
#
#     id: int = Column(Integer, primary_key=True)
#     number: int = Column(Integer, ForeignKey("wells_data.id"))
#     category_dict: dict = Column(JSON, nullable=False)
#     type_kr: str = Column(String, nullable=False)
#     work_plan: str = Column(String, nullable=False)
#     excel_json: dict = Column(JSON, nullable=False)
#     data_change_paragraph: dict = Column(JSON, nullable=False)
#     norms_time: float = Column(Float, nullable=False)
#     chemistry_need: dict = Column(JSON, nullable=False)
#     geolog_id = Column(Integer, ForeignKey('users.id'))
#     date_create: Date = Column(Date, nullable=False)
#     perforation_project: dict = Column(JSON)
#     type_absorbent: str = Column(String)
#     static_level: float = Column(Float, nullable=True)
#     dinamic_level: float = Column(Float, nullable=True)
#     expected_data: dict = Column(JSON, nullable=False)
#     curator: str = Column(String, nullable=False)
#     region: str = Column(String, nullable=False)
#     contractor: str = Column(String, nullable=False)
#
#     well_data = relationship("WellsData", back_populates="repairs")
#     users = relationship("Users", back_populates="wells_repairs")