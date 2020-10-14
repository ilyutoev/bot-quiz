import re
import os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def get_questions():
    """Открываем файл с вопросами и возвращаем словарь вопрос: ответ."""
    with open('questions.txt', 'r', encoding='KOI8-R') as f:
        questions_str = f.read()

    questions = {}
    question = ''
    for line in questions_str.split('\n\n'):
        if 'Вопрос' in line:
            question = re.sub(r'Вопрос .+:?\n', '', line).replace('\n', ' ').strip()
        if 'Ответ' in line:
            answer = line.replace('Ответ:', '').replace('\n', ' ').strip()
            questions[question] = answer

    return questions


def start(bot, update):
    """Отправка сообщения на комманду /start."""
    update.message.reply_text('Hi!')


def echo(bot, update):
    """Отвечаем пользователю его же сообщением."""
    update.message.reply_text(update.message.text)


def main():
    """Основная функция."""
    questions = get_questions()

    quiz_telegram_bot_token = os.getenv('QUIZ_TELEGRAM_BOT_TOKEN')
    updater = Updater(token=quiz_telegram_bot_token)

    start_handler = CommandHandler('start', start)
    text_handler = MessageHandler(Filters.text, echo)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(text_handler)
    updater.start_polling()


if __name__ == '__main__':
    main()
