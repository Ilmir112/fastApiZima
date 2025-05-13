from datetime import datetime
from typing import Optional

from fastapi import Depends, Request, Header, HTTPException
from jose import JWTError, jwt

from zimaApp.config import settings
from zimaApp.exceptions import (
    IncorrectTokenFormatException,
    TokenAbcentException,
    TokenExpiredException,
    UserIsNotPresentException,
)
from zimaApp.users.dao import UsersDAO
from zimaApp.users.models import Users


async def get_token(request: Request, authorization: Optional[str] = Header(None)):
    # Попытка получить токен из заголовка Authorization
    if authorization and authorization.startswith("Bearer "):
        return authorization[len("Bearer "):]

    # Если токена в заголовке нет, попробуем из cookies
    token = request.cookies.get("summary_information_access_token")
    if token:
        return token

    if not token:
        raise TokenAbcentException




async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
    except JWTError:
        raise IncorrectTokenFormatException
    expire: str = payload.get("exp")
    if (not expire) or (int(expire) < datetime.utcnow().timestamp()):
        raise TokenExpiredException
    user_id: str = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException
    user = await UsersDAO.find_by_id(int(user_id))
    if not user:
        raise UserIsNotPresentException
    return user


async def get_current_admin_user(current_user: Users = Depends(get_current_user)):
    if current_user.access_level not in ["creator", "admin"]:
        raise UserIsNotPresentException
    return current_user
