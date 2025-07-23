
from pika import ConnectionParameters, BlockingConnection
from pika.connection import URLParameters

from zimaApp.config import settings, router_broker, init_broker
from zimaApp.logger import logger

# @broker.get("/send_messenger")
# async def send_message_to_queue(body: str, QUEUE_NAME: str):
#
#     # Подключение к RabbitMQ
#     try:
#         await broker.broker.publish(
#             exchange="",
#             routing_key=QUEUE_NAME,
#             message=body
#         )
#         return {"data": "OK"}
#     except Exception as e:
#         logger.critical(e)


async def send_message_to_queue(body: str, QUEUE_NAME: str):
    try:
        await init_broker()
        await router_broker.publish(body, QUEUE_NAME)

        # parameters = URLParameters(settings.rabbitmq_url)
        # connection = BlockingConnection(parameters)
        #
        # channel = connection.channel()
        #
        # # Объявляем очередь (если еще не существует)
        # channel.queue_declare(queue=QUEUE_NAME, durable=True)
        #
        # # Публикуем сообщение
        # channel.basic_publish(
        #     exchange='',
        #     routing_key=QUEUE_NAME,
        #     body=body
        # )
        #
        # # Закрываем соединение
        # connection.close()

        return {"data": "OK"}
    except Exception as e:
        logger.critical(e)
        return {"error": str(e)}