from sqlalchemy import Column, Integer, String, Date, JSON
from zimaApp.database import Base


class WellsRepair(Base):
    __tablename__ = 'wells_repairs'

    id = Column(Integer, primary_key=True)
    well_number = Column(String, nullable=False)
    area_well = Column(String, nullable=False)
    well_oilfield = Column(String, nullable=False)
    cdng = Column(String, nullable=False)
    type_kr = Column(String, nullable=False)
    work_plan = Column(String, nullable=False)
    contractor = Column(String, nullable=False)
    geolog = Column(String, nullable=False)
    date_create = Column(Date, nullable=False)
    data_well = Column(JSON, nullable=False)
    costumer = Column(String, nullable=False)
    excel_json = Column(JSON, nullable=False)
    data_change_paragraph = Column(JSON, nullable=False)
    category_dict = Column(JSON)
    appointment = Column(String, nullable=False)
    inventory_number = Column(String)
    wellhead_fittings = Column(String)
    angle_data = Column(JSON)




