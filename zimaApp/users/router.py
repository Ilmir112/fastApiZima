from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi_cache.decorator import cache

from zimaApp.config import settings
from zimaApp.exceptions import IncorectLoginOrPassword, UserAlreadyExistsException
from zimaApp.logger import logger
from zimaApp.tasks.telegram_bot_template import TelegramInfo
from zimaApp.users.auth import authenticate_user, create_access_token, get_password_hash

from fastapi_versioning import version
from zimaApp.users.dao import UsersDAO
from zimaApp.users.dependencies import get_current_admin_user, get_current_user
from zimaApp.users.models import Users
from zimaApp.users.schemas import SUsersAuth, SUsersRegister, SUserUpdate

router = APIRouter(prefix="/auth", tags=["Auth & пользователи"])

@router.post("/register")
@version(1)
async def register_user(user_data: SUsersRegister):
    try:
        # Проверка существования пользователя по логину
        existing_user = await UsersDAO.find_one_or_none(login_user=user_data.login_user)
        if existing_user:
            # Возвращаем ошибку, если пользователь уже существует
            return {
                "status": "error",
                "error": "exists",
                "message": "Пользователь с таким логином уже существует"
            }

        # Хеширование пароля перед сохранением
        hashed_password = get_password_hash(user_data.password)

        # Добавление нового пользователя в базу данных
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
            access_level='user',
        )

        # Отправка сообщения в Telegram при продакшене
        if settings.MODE == "PROD":
            await TelegramInfo.send_message_registration_users(user_data)

        # Логирование успешной регистрации
        logger.info(
            "User registered", extra={"login": user_data.login_user}
        )

        return {
            "status": "success",
            "message": "Пользователь успешно зарегистрирован",
            "user": {
                "login": user_data.login_user
            }
        }
    except Exception as e:
        # Логирование ошибок и возврат внутренней ошибки сервера
        logger.error("Critical error during registration", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/login")
@version(1)
async def login_user(response: Response, user_data: SUsersAuth):
    try:
        user = await authenticate_user(user_data.login_user, user_data.password)
        if not user:
            raise IncorectLoginOrPassword
        access_token = create_access_token({"sub": str(user.id)})
        response.set_cookie(
            "summary_information_access_token", access_token, httponly=True
        )
        # Отправка сообщения о входе пользователя
        if settings.MODE == "PROD":
            await TelegramInfo.send_message_users(user.login_user)

        logger.info(
            "Users insert", extra={"users": user_data.login_user}, exc_info=True
        )
        return {
            "login_user": user.login_user,
            "position_id": user.position_id,
            "ctcrs": user.ctcrs,
            "contractor": user.contractor,
            "access_token": access_token,
        }
    except IncorectLoginOrPassword:
        raise IncorectLoginOrPassword
    except Exception as e:
        logger.error("Critical error", extra=e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
@version(1)
async def logout_user(response: Response):
    response.delete_cookie("summary_information_access_token")


@router.post("/update")
@version(1)
async def update_user(
        response: Response,
        user_update: SUserUpdate,
        current_user: Users = Depends(get_current_user)
):
    try:
        hashed_password = get_password_hash(user_update.password)
        user_update.password = hashed_password
        user_obj = await UsersDAO.update(filter_by={"id": current_user.id}, **user_update.dict(exclude_unset=True))

        return {
            "status": "success",
            "message": "Данные успешно обновлены",
            "user": {
                "login": user_update.login_user,
                "name": user_update.name_user,
                "surname": user_update.surname_user,
                "second_name": user_update.second_name,
                "position": user_update.position_id,
                "customer": user_update.costumer,
                "contractor": user_update.contractor,
                "ctcrs": user_update.ctcrs,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me")
@version(1)
async def read_users_me(current_user: Users = Depends(get_current_user)):
    return current_user


@router.get("/all")
@version(1)
async def read_users_all():
    return await UsersDAO.find_all()
