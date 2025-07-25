import asyncio
import json
from datetime import datetime

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import insert

from zimaApp.well_silencing.models import WellSilencing
from zimaApp.config import settings
from zimaApp.database import Base, async_session_maker, engine
from zimaApp.well_classifier.models import WellClassifier
from zimaApp.wells_repair_data.models import WellsRepair
from zimaApp.wells_data.models import WellsData
from zimaApp.main import base_app as fastapi_app
from zimaApp.users.models import Users


def open_mock_json(model: str):
    with open(f"zimaApp/tests/mock_{model}.json", encoding="utf-8") as file:
        return json.load(file)


def validate_data_in_timestamp(value_list):
    value_list_new = []
    value_dict_new = {}
    for value_dict in value_list:
        for key, value in value_dict.items():
            if isinstance(value, datetime):
                value_dict_new[key] = datetime.strptime(value, "%Y-%m-%d")
            else:
                value_dict_new[key] = value
        value_list_new.append(value_dict_new)
    return value_list_new


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        # Удаление всех заданных нами таблиц из БД
        await conn.run_sync(Base.metadata.drop_all)
        # Добавление всех заданных нами таблиц из БД
        await conn.run_sync(Base.metadata.create_all)

    silencing = validate_data_in_timestamp(open_mock_json("silencing"))
    classifier = validate_data_in_timestamp(open_mock_json("classifier"))
    users = validate_data_in_timestamp(open_mock_json("users"))
    repair = validate_data_in_timestamp(open_mock_json("repair"))
    wells_datas = validate_data_in_timestamp(open_mock_json("well_datas"))

    async with async_session_maker() as session:
        for Model, values in [
            (WellSilencing, silencing),
            (WellClassifier, classifier),
            (Users, users),
            (WellsRepair, repair),
            (WellsData, wells_datas),
        ]:
            query = insert(Model).values(values)
            await session.execute(query)

        await session.commit()


# Взято из документации к pytest-asyncio
# Создаем новый event loop для прогона тестов
@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def ac():
    "Асинхронный клиент для тестирования эндпоинтов"
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="session")
async def authenticated_ac():
    "Асинхронный аутентифицированный клиент для тестирования эндпоинтов"
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as ac:
        await ac.post(
            "/auth/login",
            json={
                "email": "test@test.com",
                "password": "test",
            },
        )
        assert ac.cookies["zima_access_token"]
        yield ac


# Фикстура оказалась бесполезной
# @pytest.fixture(scope="function")
# async def session():
#     async with async_session_maker() as session:
#         yield session
