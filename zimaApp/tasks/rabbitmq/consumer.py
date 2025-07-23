from zimaApp.config import settings, router_broker

import asyncio
import aio_pika



@router_broker.subscriber("repair_gis")
async def process_message(message: aio_pika.IncomingMessage):
    from zimaApp.main import bot
    async with message.process():  # автоматически подтверждает сообщение после блока
        body = message.body.decode()
        print(f"Received message: {body}")

        for admin in settings.CHAT_ID:
            await bot.send_message(
                chat_id=admin,
                text=message)

        # Здесь добавьте вашу логику обработки сообщения
        # Например, сохранить в базу, отправить уведомление и т.д.
        # После выхода из блока message.process() сообщение будет подтверждено и удалено из очереди

async def start_consumer():
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("repair_gis", durable=True)

        # Запуск потребителя
        await queue.consume(process_message)

        print("Начинаю слушать очередь 'repair_gis'...")
        # Чтобы слушать бесконечно, используем asyncio.Event()
        await asyncio.Event().wait()

# Запуск потребителя в основном приложении или в отдельной задаче
# Например, в вашем основном файле:
# asyncio.create_task(consume_messages())







