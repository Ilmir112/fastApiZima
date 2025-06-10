
from pydantic import BaseModel


class SWellsBrigade(BaseModel):
    id: int
    contractor: str
    costumer: str
    expedition: str
    number_brigade: int
    brigade_master: dict
    phone_number_brigade: str
    lifting_unit: str
    hydraulic_wrench: str
    weight_indicator: str
    brigade_composition: dict
    pvo_type: str
    number_pvo: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class SBrigadeSearch(BaseModel):
    number_brigade: int
    contractor: str