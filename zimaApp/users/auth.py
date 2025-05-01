from datetime import datetime, timedelta
from jose import jwt

from passlib.context import CryptContext

from .users.dao import UsersDAO
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=1800)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, settings.ALGORITHM
    )
    return encoded_jwt


async def authenticate_user(login_user: str, password: str):
    user = await UsersDAO.find_one_or_none(login_user=login_user)
    if not user and not verify_password(password, user.password):
        return None
    print(f'текущий {user}')
    return user
