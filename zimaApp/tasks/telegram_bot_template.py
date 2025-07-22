from datetime import datetime


from zimaApp.repairGis.schemas import SRepairsGis

from zimaApp.tasks.tasks import send_message
from zimaApp.config import settings, broker

import httpx

from zimaApp.wells_data.dao import WellsDatasDAO
from zimaApp.wells_data.schemas import SWellsData
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
    async def send_message_create_plan_gnkt(cls, username: str, well_number: str, well_area: str):
        message = f"Пользователь {username} создал план работ ГНКТ по {well_number} {well_area}"

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
    async def send_message_create_repair_gis(cls, result: SRepairsGis):
        wells_id = await WellsDatasDAO.find_one_or_none(id=result.well_id)
        message = f"Подрядчик по ГИС {result.contractor_gis} открыл простой по скважине " \
                  f"{wells_id.well_number} {wells_id.well_area} " \
                  f"в {result.downtime_start.strftime('%d-%m-%Y %H:%M')}. " \
                  f"по причине: {result.downtime_reason}. Телефонограмма от " \
                  f"{result.message_time.strftime('%d-%m-%Y %H:%M')}"

        try:
            await broker.connect()
            await broker.publish(message, "repair_gis")
        except Exception as e:
            print(e)

            await broker.publish(message, "repair_gis")


        payload = {
            "chat_id": settings.CHAT_ID,
            "text": message
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(TelegramInfo.URL, json=payload)
            response.raise_for_status()

    @classmethod
    async def send_message_update_brigade(cls, username: str, number_brigade: str, contractor: str):
        message = f"Пользователь {username} обновил данные бригады № {number_brigade} {contractor}"

        payload = {
            "chat_id": settings.CHAT_ID,
            "text": message
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(TelegramInfo.URL, json=payload)
            response.raise_for_status()

    @classmethod
    async def send_message_update_norms(cls, username: str, well_number: str, well_area: str):
        message = f"Пользователь {username} обновил данные АВР по id {well_number} БР {well_area}"

        payload = {
            "chat_id": settings.CHAT_ID,
            "text": message
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(TelegramInfo.URL, json=payload)
            response.raise_for_status()

    @classmethod
    async def send_message_create_norms(cls, username: str, well_number: str):
        message = f"Пользователь {username} создал АВР для скважины № {well_number}"

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