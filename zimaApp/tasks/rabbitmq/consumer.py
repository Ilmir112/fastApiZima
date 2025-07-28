import json

from zimaApp.config import settings, router_broker

import asyncio
import aio_pika

from zimaApp.logger import logger
from zimaApp.tasks.tasks import parse_telephonegram, add_telephonegram_to_db


@router_broker.subscriber("repair_gis")
async def process_message(message: aio_pika.IncomingMessage):
    from zimaApp.main import bot
    try:
        async with message.process():  # автоматически подтверждает сообщение после блока
            body = message.body.decode()
            # print(f"Received message: {body}")
            for from_address, subject, body_text, dt in json.loads(body):
                parsed_data = await parse_telephonegram(body_text, from_address, dt)
                if parsed_data:
                    return await add_telephonegram_to_db(parsed_data)
                else:
                    await bot.send_message(
                        chat_id=settings.CHAT_ID,
                        text=body_text[:600])
    except aio_pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Connection lost: {e}")
        # Здесь можно реализовать логику повторного подключения или перезапуска

    except Exception as e:
        logger.error(e)

async def start_consumer():
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("repair_gis", durable=True)

        # Запуск потребителя
        await queue.consume(process_message)

        logger.info("Начинаю слушать очередь 'repair_gis'...")
        # Чтобы слушать бесконечно, используем asyncio.Event()
        await asyncio.Event().wait()


if __name__ == '__main__':
    asyncio.run(start_consumer())
# Запуск потребителя в основном приложении или в отдельной задаче
# Например, в вашем основном файле:
# asyncio.create_task(consume_messages())
