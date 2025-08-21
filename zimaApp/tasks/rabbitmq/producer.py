import aio_pika
from celery.bin.result import result
from pika import ConnectionParameters, BlockingConnection
from pika.connection import URLParameters

from zimaApp.config import settings, router_broker, init_broker
from zimaApp.logger import logger

async def send_message_to_queue(body: str, QUEUE_NAME: str, token: str = None):
    # Создаем новое подключение при каждом вызове
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    try:
        async with connection:
            channel = await connection.channel()
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            await channel.default_exchange.publish(
                aio_pika.Message(body=body, headers=headers),
                routing_key=QUEUE_NAME
            )
        return True
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")
        return False

