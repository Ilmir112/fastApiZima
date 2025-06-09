
from zimaApp.tasks.tasks import send_message
from zimaApp.config import settings


import httpx

from zimaApp.wells_repair_data.schemas import SWellsRepair
from time import sleep


class TelegramInfo:
    URL = f"https://api.telegram.org/bot{settings.TOKEN}/sendMessage"

    @classmethod
    async def send_message_users(cls, username: str):
        message = f"Пользователь {username} вошел в систему."
        payload = {
            "chat_id": settings.CHAT_ID,
            "text": message
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(TelegramInfo.URL, json=payload)
            response.raise_for_status()

    @classmethod
    async def send_message_create_plan(cls, username: str, well_number: str, well_area: str, work_plan: str):
        message = f"Пользователь {username} создал план работ {well_number} {well_area} {work_plan}"

        payload = {
            "chat_id": settings.CHAT_ID,
            "text": message
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(TelegramInfo.URL, json=payload)
            response.raise_for_status()

    @classmethod
    async def send_message_create_brigade(cls, username: str, number_brigade: str, contractor: str):
        message = f"Пользователь {username} создал бригаду № {number_brigade} {contractor}"

        payload = {
            "chat_id": settings.CHAT_ID,
            "text": message
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(TelegramInfo.URL, json=payload)
            response.raise_for_status()

    @classmethod
    async def send_message_create_norms(cls, username: str, number_brigade: str, contractor: str):
        message = f"Пользователь {username} создал бригаду № {number_brigade} {contractor}"

        payload = {
            "chat_id": settings.CHAT_ID,
            "text": message
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(TelegramInfo.URL, json=payload)
            response.raise_for_status()

    @classmethod
    async def send_message_logger(cls, message: dict):
        payload = {
            "chat_id": settings.CHAT_ID,
            "text": message
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(TelegramInfo.URL, json=payload)
            response.raise_for_status()