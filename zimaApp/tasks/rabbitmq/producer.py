import aio_pika
from celery.bin.result import result
from pika import ConnectionParameters, BlockingConnection
from pika.connection import URLParameters

from zimaApp.config import settings, router_broker, init_broker
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
    # try:
    #     # await init_broker()
    #     # result = await router_broker.publish(body, QUEUE_NAME)
    #
    #     # parameters = URLParameters(settings.rabbitmq_url)
    #     # connection = BlockingConnection(parameters)
    #     #
    #     # channel = connection.channel()
    #     #
    #     # # Объявляем очередь (если еще не существует)
    #     # channel.queue_declare(queue=QUEUE_NAME, durable=True)
    #     #
    #     # # Публикуем сообщение
    #     # channel.basic_publish(
    #     #     exchange='',
    #     #     routing_key=QUEUE_NAME,
    #     #     body=body
    #     # )
    #     #
    #     # # Закрываем соединение
    #     # connection.close()
    #
    #     return {"data": "OK"}
    # except Exception as e:
    #     logger.critical(e)
    #     return {"error": str(e)}
