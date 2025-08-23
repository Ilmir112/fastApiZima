import json
from io import StringIO

import pandas as pd
from fastapi.params import Depends

from zimaApp.config import settings, router_broker

import asyncio
import aio_pika

from zimaApp.logger import logger

from zimaApp.tasks.tasks import parse_telephonegram, add_telephonegram_to_db, work_with_excel_summary
from zimaApp.tasks.telegram_bot_template import TelegramInfo


@router_broker.subscriber("summary_info")
async def process_read_summary(message: aio_pika.IncomingMessage):
    try:
        # Получаем тело сообщения и декодируем
        body_bytes = message.body
        body_str = body_bytes.decode('utf-8')
        if not body_str.strip():
            logger.warning("Received empty message body")
            return
        # Парсим JSON
        file_data_list = json.loads(body_str)

        # Проверка типа данных
        if not isinstance(file_data_list, list):
            logger.error("Ожидался список словарей в сообщении")
            return
        summary_count = 0
        for file_data in file_data_list:
            filename = file_data.get("filename")
            dataframe_json = file_data.get("dataframe")
            if not filename or not dataframe_json:
                logger.warning("Некорректные данные в сообщении")
                continue

            df = pd.read_json(StringIO(dataframe_json))

            # Обработка DataFrame
            result = await work_with_excel_summary(filename, df)
            if result:
                summary_count += 1

        await TelegramInfo.send_update_summary(summary_count, len(file_data_list))
        await message.ack()


    except aio_pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Connection lost: {e}")
    except Exception as e:
        logger.exception(f"Ошибка при обработке сообщения: {e}")


@router_broker.subscriber("repair_gis")
async def process_message(message: aio_pika.IncomingMessage):
    from zimaApp.main import bot_user

    try:
        async with (
            message.process()
        ):  # автоматически подтверждает сообщение после блока
            body = message.body.decode()
            if not body.strip():
                logger.warning("Received empty message body")
                return
            print(body)
            for from_address, subject, body_text, dt in json.loads(body):
                parsed_data = await parse_telephonegram(body_text, from_address, dt)
                if parsed_data:
                    return await add_telephonegram_to_db(parsed_data)
                else:
                    await bot_user.send_message(
                        chat_id=settings.CHAT_ID, text=body_text[:600]
                    )
    except json.JSONDecodeError as e:
        print(f"Ошибка при парсинге JSON: {e}")
        print(f"Данные для парсинга: {body}")
        raise
    except aio_pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Connection lost: {e}")

    except Exception as e:
        logger.error(e)


async def start_consumer():
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()

    # Объявляем очереди
    queue_repair_gis = await channel.declare_queue("repair_gis", durable=True)
    queue_summary_info = await channel.declare_queue("summary_info", durable=True)

    # Запускаем потребителей
    task1 = asyncio.create_task(queue_repair_gis.consume(process_message))
    task2 = asyncio.create_task(queue_summary_info.consume(process_read_summary))

    logger.info("Начинаю слушать очереди 'repair_gis' и 'summary_info'...")

    return task1, task2


if __name__ == "__main__":
    asyncio.run(start_consumer())
# Запуск потребителя в основном приложении или в отдельной задаче
# Например, в вашем основном файле:
# asyncio.create_task(consume_messages())
