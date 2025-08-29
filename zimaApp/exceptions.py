from fastapi import HTTPException, status


class ZimaException(HTTPException):
    status_code = 500
    detail = "Ошибка обработки запроса"

    def __init__(self, information=None):
        super().__init__(status_code=self.status_code, detail=self.detail)


class ExceptionError(ZimaException):
    status_code = 500

    def __init__(self, detail):
        super().__init__(status_code=self.status_code, detail=detail)

class UserAlreadyExistsException(ZimaException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже существует"

class WellsAlreadyExistsException(ZimaException):
    status_code = status.HTTP_409_CONFLICT
    detail = "По скважине открыт ремонт"

class BrigadeAlreadyExistsException(ZimaException):
    status_code = status.HTTP_409_CONFLICT
    detail = "На бригаду открыт ремонт"

class WellsClosedExistsException(ZimaException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Ремонт уже загружен"


class DowntimeDurationAlreadyExistsException(ZimaException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Время простоя не может быть отрицательным"


class IncorectLoginOrPassword(ZimaException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверная логин или пароль"

class IncorectLoginAdmin(ZimaException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Приложением может пользоваться только админ"


class TokenExpiredException(ZimaException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Срок действия токена истек"


class TokenAbsentException(ZimaException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен отсутствует"


class IncorrectTokenFormatException(ZimaException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный формат токена"
