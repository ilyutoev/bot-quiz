import re
import os
import random

from telegram import ReplyKeyboardMarkup
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


def text(bot, update):
    """Отвечаем на пользовательские сообщения."""

    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)

    if update.message.text == 'Новый вопрос':
        message = random.choice(list(questions))

    update.message.reply_text(message, reply_markup=reply_markup)


def main():
    """Основная функция."""

    quiz_telegram_bot_token = os.getenv('QUIZ_TELEGRAM_BOT_TOKEN')
    updater = Updater(token=quiz_telegram_bot_token)

    start_handler = CommandHandler('start', start)
    text_handler = MessageHandler(Filters.text, text)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(text_handler)
    updater.start_polling()


if __name__ == '__main__':
    questions = get_questions()

    main()
