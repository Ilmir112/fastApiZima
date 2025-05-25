from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi_cache.decorator import cache

from zimaApp.exceptions import IncorectLoginOrPassword, UserAlreadyExistsException
from zimaApp.logger import logger
from zimaApp.users.auth import authenticate_user, create_access_token, get_password_hash

from fastapi_versioning import version
from zimaApp.users.dao import UsersDAO
from zimaApp.users.dependencies import get_current_admin_user, get_current_user
from zimaApp.users.models import Users
from zimaApp.users.schemas import SUsersAuth, SUsersRegister

router = APIRouter(prefix="/auth", tags=["Auth & пользователи"])


@router.post("/register")
@version(1)
async def register_user(user_data: SUsersRegister):
    try:
        existing_user = await UsersDAO.find_one_or_none(login_user=user_data.login_user)
        if existing_user:
            raise UserAlreadyExistsException
        hashed_password = get_password_hash(user_data.password)
        await UsersDAO.add_data(
            login_user=user_data.login_user,
            name_user=user_data.name_user,
            surname_user=user_data.surname_user,
            second_name=user_data.second_name,
            position_id=user_data.position_id,
            costumer=user_data.costumer,
            contractor=user_data.contractor,
            ctcrs=user_data.ctcrs,
            password=hashed_password,
            access_level=user_data.access_level,
        )
        logger.info("Users adding", extra={"well_number": user_data.login_user}, exc_info=True)
    except Exception as e:
        logger.error('Critical error', extra=e, exc_info=True)


@router.post("/login")
@version(1)
async def login_user(response: Response, user_data: SUsersAuth):
    user = await authenticate_user(user_data.login_user, user_data.password)
    if not user:
        raise IncorectLoginOrPassword
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("summary_information_access_token", access_token, httponly=True)
    logger.info("Users insert", extra={"well_number": user_data.login_user}, exc_info=True)
    return {"login_user": user.login_user,
            "position_id": user.position_id,
            "ctcrs": user.ctcrs,
            "contractor": user.contractor,
            "access_token": access_token}


@router.post("/logout")
@version(1)
async def logout_user(response: Response):
    response.delete_cookie("summary_information_access_token")


@router.get("/me")
@version(1)
async def read_users_me(current_user: Users = Depends(get_current_user)):
    return current_user


@router.get("/all")
@version(1)
async def read_users_all():
    return await UsersDAO.find_all()
