import re
import os
import random

import redis
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


def get_redis_connect():
    """Возвращаем подключение к редису."""
    host = os.getenv('REDIS_HOST')
    port = os.getenv('REDIS_PORT')
    password = os.getenv('REDIS_PASSWORD')

    return redis.Redis(host=host, port=port, db=0, password=password)


def start(bot, update):
    """Отправка сообщения на комманду /start."""
    update.message.reply_text('Hi!')


def text(bot, update):
    """Отвечаем на пользовательские сообщения."""

    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)

    user_id = update.effective_user.id
    user_message = update.message.text
    if user_message == 'Новый вопрос':
        message = random.choice(list(questions))
        r.set(user_id, message)
    else:
        question = r.get(user_id)
        question = question.decode('utf-8')
        full_answer = questions.get(question)
        short_answer = full_answer.split('.')[0].split('(')[0]

        if user_message.lower() == short_answer.lower():
            message = "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
        else:
            message = "Неправильно... Попробуешь ещё раз?"
    update.message.reply_text(message, reply_markup=reply_markup)


def start_telegram_bot():
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

    r = get_redis_connect()

    start_telegram_bot()
