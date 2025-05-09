from sqlalchemy import JSON, Column, Date, Integer, String, Float, Boolean
from zimaApp.database import Base


class WellsData(Base):
    __tablename__ = "wells_data"

    id = Column(Integer, primary_key=True)
    well_number = Column(String, nullable=False)
    area_well = Column(String, nullable=False)
    well_oilfield = Column(String, nullable=False)
    cdng = Column(String, nullable=False)
    costumer = Column(String)
    inventory_number = Column(String)
    wellhead_fittings = Column(String)
    appointment = Column(String)
    angle_data = Column(JSON)
    column_direction = Column(JSON)
    column_conductor = Column(JSON)
    column_production = Column(JSON)
    column_additional = Column(JSON)
    bottom_hole_drill = Column(Float)
    bottom_hole_artificial = Column(Float)
    max_angle = Column(Float)
    distance_from_rotor_table = Column(Float)
    max_angle_depth = Column(Float)
    max_expected_pressure = Column(Float)
    max_admissible_pressure = Column(Float)
    rotor_altitude = Column(Float)
    perforation = Column(JSON)
    equipment = Column(JSON)
    nkt_data = Column(JSON)
    sucker_pod = Column(JSON)
    diameter_doloto_ek = Column(Float)
    last_pressure_date = Column(Date)
    date_commissioning = Column(Date)
    date_drilling_run = Column(Date)
    date_drilling_finish = Column(Date)
    leakiness = Column(JSON),
    geolog = Column(String)
    date_create = Column(Date)