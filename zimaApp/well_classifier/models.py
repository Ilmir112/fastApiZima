from sqlalchemy import Column, Date, Integer, String

from zimaApp.database import Base


class WellClassifier(Base):
    __tablename__ = "well_classifier"

    id = Column(Integer, primary_key=True)
    cdng = Column(String, nullable=False)
    well_number = Column(String, nullable=False)
    deposit_area = Column(String, nullable=False)
    oilfield = Column(String)
    category_pressure = Column(String)
    pressure_ppl = Column(String)
    pressure_gst = Column(String)
    date_measurement = Column(String)
    category_h2s = Column(String)
    h2s_pr = Column(String)
    h2s_mg_l = Column(String)
    h2s_mg_m = Column(String)
    category_gf = Column(String)
    gas_factor = Column(String)
    today = Column(Date, nullable=False)
    region = Column(String, nullable=False)
    costumer = Column(String, nullable=False)
