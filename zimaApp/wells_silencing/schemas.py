from datetime import date

from pydantic import BaseModel


class SWellsSilencing(BaseModel):
    id: int
    well_number: str
    deposit_area: str
    today: date
    region: str
    costumer: str

    class Config:
        from_attributes = True
