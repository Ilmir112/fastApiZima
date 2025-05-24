import json

from sqlalchemy import JSON, Column, Date, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship

from zimaApp.database import Base


class WellsData(Base):
    __tablename__ = "wells_data"

    id: int = Column(Integer, primary_key=True)
    well_number: str = Column(String, nullable=False)
    well_area: str = Column(String, nullable=False)
    well_oilfield: str = Column(String, nullable=False)
    cdng: str = Column(String, nullable=False)
    costumer: str = Column(String)
    inventory_number: str = Column(String)
    wellhead_fittings: str = Column(String)
    appointment: str = Column(String)
    angle_data: dict = Column(JSON)
    column_direction: dict = Column(JSON)
    column_conductor: dict = Column(JSON)
    column_production: dict = Column(JSON)
    column_additional: dict = Column(JSON)
    bottom_hole_drill = Column(Float)
    bottom_hole_artificial: float = Column(Float)
    max_angle: float = Column(Float)
    distance_from_rotor_table: float = Column(Float)
    max_angle_depth: float = Column(Float)
    max_expected_pressure: float = Column(Float)
    max_admissible_pressure: float = Column(Float)
    rotor_altitude: float = Column(Float)
    perforation: dict = Column(JSON)
    equipment: dict = Column(JSON)
    nkt_data: dict = Column(JSON)
    sucker_pod: dict = Column(JSON)
    diameter_doloto_ek: float = Column(Float)
    last_pressure_date: Date = Column(Date)
    date_commissioning: Date = Column(Date)
    date_drilling_run: Date = Column(Date)
    date_drilling_finish: Date = Column(Date)
    leakiness: dict = Column(JSON)
    geolog: str = Column(String)
    date_create: Date = Column(Date)
    contractor: str = Column(String)

    repairs = relationship("WellsRepair", back_populates="well_data", cascade="all, delete")


