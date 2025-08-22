from datetime import datetime


from zimaApp.repairGis.schemas import SRepairsGis
from zimaApp.tasks.rabbitmq.producer import send_message_to_queue

from zimaApp.tasks.tasks import send_message
from zimaApp.config import settings

import httpx

from zimaApp.users.schemas import SUsersRegister
from zimaApp.wells_data.dao import WellsDatasDAO
from zimaApp.wells_data.schemas import SWellsData
from zimaApp.wells_repair_data.schemas import SWellsRepair
from time import sleep


class TelegramInfo:
    URL = f"https://api.telegram.org/bot{settings.TOKEN}/sendMessage"

    @classmethod
    async def send_message_users(cls, username: str):
        message = f"Пользователь {username} вошел в систему."
        if username != 'Зуфаров И.М.':
            payload = {"chat_id": settings.CHAT_ID, "text": message}
            # await send_message(message, settings.CHAT_ID)
            async with httpx.AsyncClient() as client:
                response = await client.post(TelegramInfo.URL, json=payload)
                response.raise_for_status()

    @classmethod
    async def send_message_registration_users(cls, username: SUsersRegister):
        message = (f"Пользователь {username.position_id} "
                   f"{username.surname_user} {username.name_user} зарегистрировался.")
        payload = {"chat_id": settings.CHAT_ID, "text": message}
        # await send_message(message, settings.CHAT_ID)
        async with httpx.AsyncClient() as client:
            response = await client.post(TelegramInfo.URL, json=payload)
            response.raise_for_status()

    @classmethod
    async def send_message_create_plan(
        cls, username: str, well_number: str, well_area: str, work_plan: str
    ):
        message = f"Пользователь {username} создал план работ {well_number} {well_area} {work_plan}"

        payload = {"chat_id": settings.CHAT_ID, "text": message}
        async with httpx.AsyncClient() as client:
            response = await client.post(TelegramInfo.URL, json=payload)
            response.raise_for_status()

    @classmethod
    async def send_message_add_plan_pdf(
            cls, username: str, well_number: str, well_area: str
    ):
        message = f"Пользователь {username} добавил план работ в PDF {well_number} {well_area}"

        payload = {"chat_id": settings.CHAT_ID, "text": message}
        async with httpx.AsyncClient() as client:
            response = await client.post(TelegramInfo.URL, json=payload)
            response.raise_for_status()

    @classmethod
    async def send_message_create_plan_gnkt(
        cls, username: str, well_number: str, well_area: str
    ):
        message = f"Пользователь {username} создал план работ ГНКТ по {well_number} {well_area}"

        payload = {"chat_id": settings.CHAT_ID, "text": message}
        async with httpx.AsyncClient() as client:
            response = await client.post(TelegramInfo.URL, json=payload)
            response.raise_for_status()

    @classmethod
    async def send_message_create_brigade(
        cls, username: str, number_brigade: str, contractor: str
    ):
        message = (
            f"Пользователь {username} создал бригаду № {number_brigade} {contractor}"
        )

        payload = {"chat_id": settings.CHAT_ID, "text": message}
        async with httpx.AsyncClient() as client:
            response = await client.post(TelegramInfo.URL, json=payload)
            response.raise_for_status()

    @classmethod
    async def send_message_update_classification(
            cls, results: str):
        message = (
            f"Добавлено {len(results)} скважин в классификатор"
        )

        payload = {"chat_id": settings.CHAT_ID, "text": message}
        async with httpx.AsyncClient() as client:
            response = await client.post(TelegramInfo.URL, json=payload)
            response.raise_for_status()

    @classmethod
    async def send_message_create_repair_gis(cls, result: SRepairsGis):
        wells_id = await WellsDatasDAO.find_one_or_none(id=result.well_id)
        message = (
            f"Подрядчик по ГИС {result.contractor_gis} открыл простой по скважине "
            f"{wells_id.well_number} {wells_id.well_area} "
            f"в {result.downtime_start.strftime('%d-%m-%Y %H:%M')}. "
            f"по причине: {result.downtime_reason}. Телефонограмма от "
            f"{result.message_time.strftime('%d-%m-%Y %H:%M')}"
        )

        payload = {"chat_id": settings.CHAT_ID, "text": message}
        async with httpx.AsyncClient() as client:
            response = await client.post(TelegramInfo.URL, json=payload)
            response.raise_for_status()

    @classmethod
    async def send_message_update_brigade(
        cls, username: str, number_brigade: str, contractor: str
    ):
        message = f"Пользователь {username} обновил данные бригады № {number_brigade} {contractor}"

        payload = {"chat_id": settings.CHAT_ID, "text": message}
        async with httpx.AsyncClient() as client:
            response = await client.post(TelegramInfo.URL, json=payload)
            response.raise_for_status()

    @classmethod
    async def send_message_update_norms(
        cls, username: str, well_number: str, well_area: str
    ):
        message = f"Пользователь {username} обновил данные АВР по id {well_number} БР {well_area}"

        payload = {"chat_id": settings.CHAT_ID, "text": message}
        async with httpx.AsyncClient() as client:
            response = await client.post(TelegramInfo.URL, json=payload)
            response.raise_for_status()

    @classmethod
    async def send_message_create_norms(cls, username: str, well_number: str):
        message = f"Пользователь {username} создал АВР для скважины № {well_number}"

        payload = {"chat_id": settings.CHAT_ID, "text": message}
        async with httpx.AsyncClient() as client:
            response = await client.post(TelegramInfo.URL, json=payload)
            response.raise_for_status()

    @classmethod
    async def send_message_logger(cls, message: dict):
        payload = {"chat_id": settings.CHAT_ID, "text": message}
        async with httpx.AsyncClient() as client:
            response = await client.post(TelegramInfo.URL, json=payload)
            response.raise_for_status()
