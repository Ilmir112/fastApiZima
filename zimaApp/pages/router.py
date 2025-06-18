from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from zimaApp.pages.dao import ChangeExcelToHtml
from zimaApp.wells_repair_data.router import find_well_filter_by_number, find_wells_in_repairs, find_work_plan_all

router = APIRouter(
    prefix="/pages",
    tags=["Фронтенд"],
)

templates = Jinja2Templates(directory="zimaApp/templates")


@router.get("/plan_work")
async def get_avr_page(
        request: Request,
        wells_repair=Depends(find_work_plan_all)
):
    excel_answer = ChangeExcelToHtml.change_method(wells_repair[0].excel_json)

    return templates.TemplateResponse(
        name="work_plan.html", context={
        "request": request,
        "wells_repair": excel_answer

        })
