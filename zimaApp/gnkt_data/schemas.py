from typing import Dict, Any, Literal, Optional, Union
from datetime import date

from pydantic import BaseModel, confloat, constr, conint


class SGnktData(BaseModel):

    gnkt_number: str
    well_number: str
    well_area: str
    contractor: Optional[str]
    length_gnkt: Optional[Union[confloat(ge=70, le=5000), conint(ge=70, le=5000)]] = (
        None
    )
    diameter_gnkt: Optional[Union[confloat(ge=30, le=50), conint(ge=30, le=50)]] = None
    wear_gnkt: Optional[Union[float, int]] = None
    mileage_gnkt: Optional[Union[float, int]]
    tubing_fatigue: Optional[Union[float, int]] = None
    previous_well: Optional[str]
    date_repair: Optional[date]
    pvo_number: Optional[int]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
