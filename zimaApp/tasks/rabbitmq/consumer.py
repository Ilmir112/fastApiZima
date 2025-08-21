import json

from fastapi.params import Depends

from zimaApp.config import settings, router_broker

import asyncio
import aio_pika

from zimaApp.logger import logger

from zimaApp.tasks.tasks import parse_telephonegram, add_telephonegram_to_db, work_with_excel_summary
from zimaApp.users.dependencies import get_current_user
from zimaApp.users.models import Users


@router_broker.subscriber("summary_info")
async def process_read_summary(message:aio_pika.IncomingMessage):
    try:
        print(message)
        for file_data in message:
            well_data = await work_with_excel_summary(file_data["filename"], file_data["dataframe"])
            if well_data:
                logger.info(f"сводка по скважине {well_data.well_number} обновлена")
    except aio_pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Connection lost: {e}")

    except Exception as e:
        logger.error(e)


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

    try:        # Ожидаем завершения задач (они работают бесконечно)
        await asyncio.gather(task1, task2)
    except asyncio.CancelledError:
        pass
    finally:
        await connection.close()

    logger.info("Начинаю слушать очереди 'repair_gis' и 'summary_info'...")

# В основном файле запуска
if __name__ == "__main__":
    asyncio.run(start_consumer())


if __name__ == "__main__":
    asyncio.run(start_consumer())
# Запуск потребителя в основном приложении или в отдельной задаче
# Например, в вашем основном файле:
# asyncio.create_task(consume_messages())
