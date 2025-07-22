import email
import imaplib
from email.header import decode_header

import aio_pika

from zimaApp.config import settings, broker


@broker.subscriber("repair_gis")
async def send_booking_msg(msg: str):
    from zimaApp.main import bot

    for admin in settings.CHAT_ID:
        await bot.send_message(admin, text=msg)


async def send_message_to_queue(body: str, QUEUE_NAME):
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body.encode()),
            routing_key=QUEUE_NAME,
        )


