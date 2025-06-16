from datetime import datetime, date

from sqlalchemy import JSON, Column, Date, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from typing import Optional, Literal

from zimaApp.database import Base


class NormsWork(Base):
    __tablename__ = 'norms'

    id = Column(Integer, primary_key=True, autoincrement=True)
    repair_id = Column(Integer, ForeignKey("wells_repairs.id"))
    start_well_repair = Column(DateTime, nullable=False)
    repair_well_repair = Column(DateTime)
    type_tkrs = Column(String, nullable=False)
    summary_work = Column(JSON, nullable=False)
    norms_json = Column(JSON, nullable=False)
    creater_id = Column(Integer, ForeignKey("users.id"))
    lifting_unit = Column(String, nullable=False)
    number_brigade = Column(String, nullable=False)
    norms_time = Column(Float, nullable=False)
    date_create = Column(Date, default=date.today)

    well_repair = relationship("WellsRepair", back_populates="norms")
    users = relationship("Users", back_populates="norms_repairs")

    def __repr__(self):
        return f"<NormsWork(id={self.id}, repair_id={self.repair_id}, start_well_repair={self.start_well_repair}," \
               f" type_tkrs={self.type_tkrs})>"