import json

import aio_pika


from zimaApp.config import settings
from zimaApp.logger import logger


async def send_message_to_queue(body: str, QUEUE_NAME: str):
    # Создаем новое подключение при каждом вызове
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    try:
        async with connection:
            channel = await connection.channel()
            await channel.default_exchange.publish(
                aio_pika.Message(body=body), routing_key=QUEUE_NAME
            )
        return True
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")
        return False

