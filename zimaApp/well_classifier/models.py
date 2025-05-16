from sqlalchemy import Column, Date, Integer, String

from zimaApp.database import Base


class WellClassifier(Base):
    __tablename__ = "well_classifier"

    id: int = Column(Integer, primary_key=True)
    cdng: str = Column(String, nullable=False)
    well_number: str = Column(String, nullable=False)
    well_area: str = Column(String, nullable=False)
    oilfield: str = Column(String)
    category_pressure: str = Column(String)
    pressure_ppl: str = Column(String)
    pressure_gst: str = Column(String)
    date_measurement: str = Column(String)
    category_h2s: str = Column(String)
    h2s_pr: str = Column(String)
    h2s_mg_l: str = Column(String)
    h2s_mg_m: str = Column(String)
    category_gf: str = Column(String)
    gas_factor: str = Column(String)
    today: Date = Column(Date, nullable=False)
    region: str = Column(String, nullable=False)
    costumer: str = Column(String, nullable=False)
