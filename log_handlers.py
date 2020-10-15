import logging
import telegram


class LogsToTelegramHandler(logging.Handler):
    """Обработчик логов, который шлет их в телеграм канал."""
    def __init__(self, telegram_token, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.log_bot = telegram.Bot(token=telegram_token)

    def emit(self, record):
        log_entry = self.format(record)
        self.log_bot.send_message(
            chat_id=self.chat_id, text=log_entry,
            disable_web_page_preview=True
        )
