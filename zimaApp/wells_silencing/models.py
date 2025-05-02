from sqlalchemy import Column, Integer, String, Date

from zimaApp.database import Base


class WellSilencing(Base):
    __tablename__ = 'wells_silencing'

    id = Column(Integer, primary_key=True)
    well_number = Column(String, nullable=False)
    deposit_area = Column(String, nullable=False)
    today = Column(Date, nullable=False)
    region = Column(String, nullable=False)
    costumer = Column(String, nullable=False)