from datetime import datetime, date

from sqlalchemy import JSON, Column, Date, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from typing import Optional, Literal

from zimaApp.database import Base


class NormsWork(Base):
    __tablename__ = 'norms'

    id: int = Column(Integer, primary_key=True)
    repair_id: int = Column(Integer, ForeignKey("wells_repairs.id"))
    start_well_repair: datetime = Column(DateTime, nullable=False)
    repair_well_repair: datetime = Column(DateTime)
    type_tkrs: str = Column(String)
    summary_work: dict = Column(JSON)
    norms_json: dict = Column(JSON)
    creater_id: int = Column(Integer, ForeignKey("users.id"))
    lifting_unit: str = Column(String)
    date_create: date = date.today()

    well_repair = relationship("WellsRepair", back_populates="norms")
    users = relationship("Users", back_populates="norms_repairs")

    def __repr__(self):
        return f"<NormsWork(id={self.id}, repair_id={self.repair_id}, start_well_repair={self.start_well_repair}," \
               f" type_tkrs={self.type_tkrs})>"