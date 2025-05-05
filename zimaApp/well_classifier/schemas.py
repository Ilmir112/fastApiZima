from datetime import date

from pydantic import BaseModel, conlist


class SWellClassifier(BaseModel):
    id: int
    cdng: str
    well_number: str
    deposit_area: str
    oilfield: str
    category_pressure: str
    pressure_ppl: str
    pressure_gst: str
    date_measurement: str
    category_h2s: str
    h2s_pr: str
    h2s_mg_l: str
    h2s_mg_m: str
    category_gf: str
    gas_factor: str
    today: date
    region: str
    costumer: str

    class Config:
        from_attributes = True


class SWellsClassifierCreate(BaseModel):
    cdng: str
    well_number: str
    deposit_area: str
    oilfield: str
    category_pressure: str
    pressure_ppl: str
    pressure_gst: str
    date_measurement: str
    category_h2s: str
    h2s_pr: str
    h2s_mg_l: str
    h2s_mg_m: str
    category_gf: str
    gas_factor: str
    today: date
    region: str
    costumer: str


class SWellsClassifierRegion(BaseModel):
    region: str


class SWellsClassifierBatch(BaseModel):
    data: conlist(SWellsClassifierCreate, min_length=1)
