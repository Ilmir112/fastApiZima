from sqlalchemy import Column, Integer, String, DateTime, Float

from zimaApp.database import Base


class RepairData(Base):
    __tablename__ = 'repair_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contractor = Column(String)
    brigade_number = Column(String)
    well_area = Column(String)
    well_number = Column(String)
    begin_time = Column(DateTime(timezone=True))
    finish_time = Column(DateTime(timezone=True), nullable=True)
    category_repair = Column(String, nullable=True)
    duration_repair = Column(Float, nullable=True)
    repair_code = Column(String, unique=True, nullable=False)
    type_repair = Column(String, nullable=True)

    bush = Column(String, nullable=True)