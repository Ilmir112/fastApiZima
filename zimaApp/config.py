from pydantic import ValidationError, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DATABASE_URL: str = None

    @model_validator(mode="after")
    @classmethod
    def get_database_url(cls, instance):
        # Формируем строку подключения к базе данных
        instance.DATABASE_URL = (
            f"postgresql+asyncpg://{instance.DB_USER}:{instance.DB_PASSWORD}@{instance.DB_HOST}:"
            f"{instance.DB_PORT}/{instance.DB_NAME}"
        )
        return instance

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str

    REDIS_HOST: str
    REDIS_PORT: int

    SECRET_KEY: str
    ALGORITHM: str

    class Config:
        env_file = "zimaApp/.env"
        # env_file = '.env'


try:
    # Создайте экземпляр класса Settings
    settings = Settings()
    # Для проверки
except ValidationError as e:
    print(f"Ошибка валидации: {e}")
    print(e)

# Дальнейшая логика вашего приложения...
# Добавим поле DATABASE_URL
