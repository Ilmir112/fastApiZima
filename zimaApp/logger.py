from zimaApp.config import settings
import threading
import asyncio
from queue import Queue
import logging
from telegram import Bot

# Класс для отправки сообщений в Telegram
class TelegramSender:
    def __init__(self, token):
        self.bot = Bot(token)
        self.queue = Queue()
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._worker)
        self.thread.daemon = True
        self.thread.start()

    def _worker(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._send_messages())

    async def _send_messages(self):
        while True:
            chat_id, text = self.queue.get()
            try:
                await self.bot.send_message(chat_id=chat_id, text=text)
            except Exception as e:
                # Обработка ошибок при отправке
                pass

    def send(self, chat_id, text):
        self.queue.put((chat_id, text))

# Класс обработчика логов для Telegram
class TelegramHandler(logging.Handler):
    def __init__(self, sender: TelegramSender, chat_id):
        super().__init__()
        self.sender = sender
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        # Отправляем только ERROR и выше
        if record.levelno >= logging.ERROR:
            self.sender.send(self.chat_id, log_entry)

# Инициализация отправителя и логгера
sender = TelegramSender(settings.TOKEN)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Уровень глобально — DEBUG

# Обработчик для ошибок (отправка в Telegram и вывод в консоль)
telegram_handler = TelegramHandler(sender, settings.CHAT_ID)
telegram_handler.setLevel(logging.ERROR)  # Только ERROR и выше

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
telegram_handler.setFormatter(formatter)

# Обработчик для вывода всех сообщений в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # INFO и выше (можно изменить по необходимости)
console_handler.setFormatter(formatter)

# Добавляем обработчики к логгеру
logger.addHandler(telegram_handler)
logger.addHandler(console_handler)

# Теперь:
# - ERROR и выше будут идти и в консоль, и в телеграм.
# - INFO и ниже — только в консоль.