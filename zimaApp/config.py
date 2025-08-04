import urllib
from typing import Literal

from faststream.rabbit import RabbitBroker
from pydantic import ValidationError, ConfigDict
from pydantic_settings import BaseSettings
from urllib.parse import quote


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", ""]
    LOG_LEVEL: Literal["DEV", "TEST", "PROD", "INFO"]
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    MONGO_DB_USER: str
    MONGO_DB_PASSWORD: str
    MONGO_DB_HOST: str
    MONGO_DB_PORT: int
    MONGO_DB_NAME: str

    # DATABASE_URL: str = None

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def MONGO_DATABASE_URL(self):
        return (
            f"mongodb://{self.MONGO_DB_USER}:{urllib.parse.quote(self.MONGO_DB_PASSWORD)}@"
            f"{self.MONGO_DB_HOST}:{self.MONGO_DB_PORT}/{self.MONGO_DB_NAME}"
        )

    TEST_DB_USER: str
    TEST_DB_PASSWORD: str
    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_NAME: str

    @property
    def TEST_DATABASE_URL(self):
        return (
            f"postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASSWORD}@"
            f"{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"
        )

    IMAP_SERVER: str
    EMAIL_ACCOUNT: str
    PASSWORD: str

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str

    RABBITMQ_USERNAME: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    VHOST: str

    @property
    def rabbitmq_url(self) -> str:
        return (
            f"amqp://{self.RABBITMQ_USERNAME}:{quote(self.RABBITMQ_PASSWORD)}@"
            f"{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/{self.VHOST}"
        )

    REDIS_HOST: str
    REDIS_PORT: int

    HAWK_DSN: str
    SESSION_COOKIE_SECRET: str

    SECRET_KEY: str
    ALGORITHM: str

    TOKEN: str
    TOKEN_USERS: str
    CHAT_ID: str
    EMAIL_CHECK_LIST: list

    model_config = ConfigDict(env_file=".env")
    # model_config = ConfigDict(env_file='../.env')


# В асинхронной функции
async def init_broker():
    await router_broker.connect()


try:
    # Создайте экземпляр класса Settings
    settings = Settings()

    # Создание брокера сообщений RabbitMQ
    router_broker = RabbitBroker(url=settings.rabbitmq_url)

    # Для проверки
except ValidationError as e:
    print(f"Ошибка валидации: {e}")
    print(e)
