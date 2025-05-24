import json
from datetime import date

from sqlalchemy import JSON, Column, Date, Integer, String, Float, Boolean
from zimaApp.database import Base


class GnktData(Base):
    __tablename__ = "gnkt_data"

    id: int = Column(Integer, primary_key=True)
    gnkt_number: str = Column(String, nullable=False)
    well_number: str = Column(String, nullable=False)
    well_area: str = Column(String, nullable=False)
    contractor: str = Column(String, nullable=False)
    length_gnkt: int = Column(Integer, nullable=False)
    diameter_gnkt: float = Column(Float, nullable=False)
    wear_gnkt: float = Column(Float, nullable=False)
    mileage_gnkt: int = Column(Integer, nullable=False)
    tubing_fatigue: float = Column(Float, nullable=False)
    previous_well: str = Column(String, nullable=False)
    date_repair: date = Column(Date, nullable=False)
    pvo_number: int = Column(Integer, nullable=False)
