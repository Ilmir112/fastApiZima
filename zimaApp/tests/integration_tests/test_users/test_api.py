import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "login_user,name_user,surname_user,second_name,position_id,costumer,"
    "contractor,ctcrs,password,access_level,status_code",
    [
        (
            "Ilmir112",
            "Ильмир",
            "Зуфаров",
            "Мияссарович",
            "Зам",
            "БНД",
            "Ойл",
            "ЦТРКС",
            "256",
            "GOD",
            409,
        ),
        (
            "Ilmir112",
            "Ильмир",
            "Зуфаров",
            "Мияссарович",
            "Зам",
            "БНД",
            "Ойл",
            "ЦТРКС",
            "6589",
            "GOD",
            409,
        ),
        (
            "Ilmir12",
            122,
            "Зуфарв",
            "Миясарович",
            "Замг",
            "БНД ",
            "Ойл ",
            "ЦТРКС №1",
            "1268746",
            "GOD",
            422,
        ),
        (
            "Ilmir12",
            "Ильмир",
            11,
            "Миясарович",
            "Замг",
            "БНД ",
            "Ойл ",
            "ЦТРКС №1",
            "9631",
            "GOD",
            422,
        ),
        (
            "Ilmir12",
            "Ильмир",
            "Зуфарв",
            125,
            "Замг",
            "БНД ",
            "Ойл ",
            "ЦТРКС №1",
            "964",
            "GOD",
            422,
        ),
    ],
)
async def test_register_user(
    login_user,
    name_user,
    surname_user,
    second_name,
    position_id,
    costumer,
    contractor,
    ctcrs,
    password,
    access_level,
    status_code,
    ac: AsyncClient,
):
    response = await ac.post(
        "/auth/register",
        json={
            "login_user": login_user,
            "name_user": name_user,
            "surname_user": surname_user,
            "second_name": second_name,
            "position_id": position_id,
            "costumer": costumer,
            "contractor": contractor,
            "ctcrs": ctcrs,
            "password": password,
            "access_level": access_level,
        },
    )
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "login_user,password,status_code",
    [("Ilmir112", "1953", 200), ("Ilmir112", "256", 401)],
)
async def test_login_user(login_user, password, status_code, ac: AsyncClient):
    response = await ac.post(
        "/auth/login", json={"login_user": login_user, "password": password}
    )
    assert response.status_code == status_code
