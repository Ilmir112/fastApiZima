from fastapi import HTTPException, status


class BooksException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(BooksException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже существует"


class IncorectLoginOrPassword(BooksException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверная логин или пароль"


class TokenExpiredException(BooksException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Срок действия токена истек"


class TokenAbsentException(BooksException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен отсутствует"


class IncorrectTokenFormatException(BooksException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный формат токена"