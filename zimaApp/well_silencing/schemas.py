from datetime import date

from pydantic import BaseModel, conlist


class SWellsSilencing(BaseModel):
    id: int
    well_number: str
    deposit_area: str
    today: date
    region: str
    costumer: str

    class Config:
        from_attributes = True


class SWellsSilencingCreate(BaseModel):
    well_number: str
    deposit_area: str
    today: date
    region: str
    costumer: str


class SWellsSilencingRegion(BaseModel):
    region: str


class SWellsSilencingBatch(BaseModel):
    data: conlist(SWellsSilencingCreate, min_length=1)
