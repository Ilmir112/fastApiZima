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
