from sqlalchemy import Column, Date, Integer, String

from zimaApp.database import Base


class WellSilencing(Base):
    __tablename__ = "wells_silencing"

    id: int = Column(Integer, primary_key=True)
    well_number: str = Column(String, nullable=False)
    well_area: str = Column(String, nullable=False)
    today: Date = Column(Date, nullable=False)
    region: str = Column(String, nullable=False)
    costumer: str = Column(String, nullable=False)
