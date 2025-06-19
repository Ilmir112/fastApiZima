from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates


from zimaApp.norms.router import find_norms_one
from zimaApp.pages.dao import ChangeExcelToHtml
from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users
from zimaApp.wells_repair_data.router import find_well_filter_by_number, find_wells_in_repairs, find_work_plan_all

router = APIRouter(
    prefix="/pages",
    tags=["Фронтенд"],
)

templates = Jinja2Templates(directory="zimaApp/templates")


@router.get("/plan_work")
async def get_plan_page(
        request: Request,
        wells_repair=Depends(find_work_plan_all),
        user: Users = Depends(get_current_user)
):
    excel_answer = ChangeExcelToHtml.change_method(wells_repair[0].excel_json)

    return templates.TemplateResponse(
        "work_plan.html", context={
        "request": request,
        "wells_repair": excel_answer

        })

@router.get("/norms")
async def get_norms_page(
        request: Request,
        wells_repair=Depends(find_norms_one),
        user: Users = Depends(get_current_user)
):
    excel_answer = ChangeExcelToHtml.change_method(wells_repair.norms_json)

    return templates.TemplateResponse(
        name="work_plan.html", context={
        "request": request,
        "wells_repair": excel_answer

        })
