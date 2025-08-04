from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from zimaApp.logger import logger
from fastapi_cache.decorator import cache
from fastapi_versioning import version
from zimaApp.norms.router import find_norms_one
from zimaApp.pages.dao import ChangeExcelToHtml
from fastapi.responses import HTMLResponse

from zimaApp.repairGis.router import get_repair_gis_all
from zimaApp.users.auth import authenticate_user
from zimaApp.users.dependencies import get_current_user, get_current_admin_user
from zimaApp.users.models import Users
from zimaApp.users.router import login_user
from zimaApp.wells_repair_data.router import (
    find_work_plan_all,
    find_repair_filter_by_number,
    find_repair_id,
)

router = APIRouter(
    prefix="/pages",
    tags=["Фронтенд"],
)

templates = Jinja2Templates(directory="zimaApp/templates")
# templates = Jinja2Templates(directory="templates")


@router.get("/login")
@version(1)
async def get_home_page(request: Request):
    return templates.TemplateResponse("home.html", context={"request": request})


@router.get("/repair_gis", response_class=HTMLResponse)
@version(1)
async def get_repair_gis(request: Request, repairs=Depends(get_repair_gis_all)):
    repair_url = request.url_for("repairs_gis")
    return templates.TemplateResponse(
        "repair_gis.html",
        context={"request": request, "repair_url": repair_url, "repairs": repairs},
    )


@router.get("/home", response_class=HTMLResponse)
@version(1)
async def get_home_page(request: Request):
    try:
        template = templates.TemplateResponse(
            "home.html", context={"request": request, "title": "Главная страница"}
        )
        return template
    except Exception as e:
        logger.error(e)


@router.get("/plan")
@version(1)
async def get_repair_list(request: Request, user: Users = Depends(get_current_user)):
    return templates.TemplateResponse("plan.html", context={"request": request})


@router.get("/find_repair_list")
@version(1)
async def get_repair_list(
    request: Request,
    wells_repair=Depends(find_repair_filter_by_number),
    user: Users = Depends(get_current_user),
):
    return templates.TemplateResponse(
        "plan.html", context={"request": request, "wells_repair": wells_repair}
    )


@router.get("/plan_work")
@version(1)
async def get_plan_page(
    request: Request,
    wells_repair=Depends(find_repair_id),
    user: Users = Depends(get_current_user),
):
    excel_answer = ChangeExcelToHtml.change_method(wells_repair.excel_json)

    try:
        return templates.TemplateResponse(
            "work_plan.html", context={"request": request, "wells_repair": excel_answer}
        )
    except Exception as e:
        # Обработка ошибок при рендеринге шаблона
        logger.error(f"Ошибка при рендеринге шаблона: {e}")

        print(f"Ошибка при рендеринге шаблона: {e}")
        # Можно вернуть ошибку или fallback страницу
        return templates.TemplateResponse(
            "error.html",
            context={
                "request": request,
                "error_message": "Произошла ошибка при отображении страницы.",
            },
        )


@router.get("/norms")
@version(1)
async def get_norms_page(
    request: Request,
    wells_repair=Depends(find_norms_one),
    user: Users = Depends(get_current_user),
):
    excel_answer = ChangeExcelToHtml.change_method(wells_repair.norms_json)

    return templates.TemplateResponse(
        name="work_plan.html",
        context={"request": request, "wells_repair": excel_answer},
    )
