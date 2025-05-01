from pydantic_settings import BaseSettings
from pydantic import ValidationError, model_validator


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
        instance.DATABASE_URL = f"postgresql+asyncpg://{instance.DB_USER}:{instance.DB_PASSWORD}@{instance.DB_HOST}:" \
                                f"{instance.DB_PORT}/{instance.DB_NAME}"
        return instance

    SECRET_KEY: str
    ALGORITHM: str

    class Config:
        env_file = '.env'



try:
    # Создайте экземпляр класса Settings
    settings = Settings()
      # Для проверки
except ValidationError as e:
    print("Ошибка валидации:")
    print(e)

# Дальнейшая логика вашего приложения...
 # Добавим поле DATABASE_URL


