from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext
from starlette.requests import Request


from zimaApp.users.dao import UsersDAO

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    from zimaApp.config import settings
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=1800)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt


async def authenticate_user(login_user: str, password: str):
    user = await UsersDAO.find_one_or_none(login_user=login_user)

    if user:
        if not verify_password(password, user.password):
            return None

    return user

async def authenticate(request: Request) -> bool:
    token = request.session.get("token")

    if not token:
        return False
    return True
