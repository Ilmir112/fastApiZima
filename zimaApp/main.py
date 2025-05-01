import uvicorn
from fastapi import FastAPI, Query, Depends
from typing import Optional
from datetime import date
from pydantic import BaseModel, json

from well_classifier.router import router as classifier_router
app = FastAPI()

app.include_router(classifier_router)

class WellsSearchArgs:
    def __init__(
            self,
            well_number: str,
            well_area: str,
            date_today: date
    ):
        self.well_number = well_number
        self.well_area = well_area
        self.date_today = date_today


class SWellClassifier(BaseModel):
    well_number: str
    well_area: str
    date_today: date


@app.get("/get_well_classifier/{name_id}")
async def get_well_classifier(
        search_args: WellsSearchArgs = Depends()
):

    wells = [
        {
        "well_number": "873",
        "well_area": "Игровская",
        "date_today" : "2025-04-29"
        }]
    return search_args


# class SRepairData(BaseModel):
#     well_number: str
#     area_well: str
#     well_oilfield: str
#     appointment:str
#     inv_number:str
#     wellhead_fittings:str
#     data_well: json
#     excel_json: json
#     contractor: str
#     costumer: str
#     work_plan: str
#     geolog: str
#     type_kr: str
#     data_change_paragraph: json
#     cdng: str
#     category_dict: json
#     angle_data: json
#     today: date


# @app.post("/repair_data")
# async def add_repair_data(repair_datas: SRepairData):
#     return pass

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)