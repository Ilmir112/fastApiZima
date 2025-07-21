import email
import imaplib
from email.header import decode_header

import aio_pika
from faststream.rabbit import RabbitBroker

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

async def check_emails():
    try:
        mail = imaplib.IMAP4_SSL(settings.IMAP_SERVER)
        mail.login(settings.EMAIL_ACCOUNT, settings.PASSWORD)
        mail.select("inbox")

        subject_search = 'Телефонограмма'

        # Формируем запрос как байтовую строку
        search_criteria = '(SUBJECT "{}")'.format(subject_search)
        search_bytes = search_criteria.encode('utf-8')

        # Выполняем поиск
        status, messages = mail.search(None, search_bytes)

        email_ids = messages[0].split()

        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg_bytes = response_part[1]
                    msg = email.message_from_bytes(msg_bytes)
                    subject_header = decode_header(msg["Subject"])[0]
                    subject, encoding = subject_header
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8")
                    # Обработка тела письма
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body_bytes = part.get_payload(decode=True)
                                charset = part.get_content_charset() or "utf-8"
                                body_text = body_bytes.decode(charset)
                                await send_message_to_queue(body_text)
                    else:
                        body_bytes = msg.get_payload(decode=True)
                        charset = msg.get_content_charset() or "utf-8"
                        body_text = body_bytes.decode(charset)
                        await send_message_to_queue(body_text)

        mail.logout()
    except Exception as e:
        print(e)


