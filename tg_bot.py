import re
import os
import random
from enum import Enum

import redis
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler


class State(Enum):
    QUESTION = 1
    ANSWER = 2
    GIVE_UP = 3


class Button(Enum):
    QUESTION = 'Новый вопрос'
    GIVE_UP = 'Сдаться'
    MY_SCORE = 'Мой счет'


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
    custom_keyboard = [[Button.QUESTION.value, Button.GIVE_UP.value], [Button.MY_SCORE.value]]

    reply_markup = ReplyKeyboardMarkup(custom_keyboard)

    update.message.reply_text('Привет!', reply_markup=reply_markup)

    return State.QUESTION


def handle_new_question_request(bot, update):
    """Обрабатываем запрос на отправку нового вопроса."""
    user_id = f'tg-{update.effective_user.id}'
    message = random.choice(list(questions))
    r.set(user_id, message)
    update.message.reply_text(message)

    return State.ANSWER


def handle_solution_attempt(bot, update):
    """Обработка ответа на вопрос."""

    user_id = f'tg-{update.effective_user.id}'
    user_message = update.message.text

    question = r.get(user_id)
    question = question.decode('utf-8')
    full_answer = questions.get(question)
    short_answer = full_answer.split('.')[0].split('(')[0]

    if user_message.lower() == short_answer.lower():
        message = "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
        state = State.QUESTION
    else:
        message = "Неправильно... Попробуешь ещё раз?"
        state = State.ANSWER

    update.message.reply_text(message)

    return state


def handle_give_up(bot, update):
    """Кнопка сдаться. Печатаем ответ на вопрос и присылаем следующий вопрос."""
    user_id = f'tg-{update.effective_user.id}'

    question = r.get(user_id)
    question = question.decode('utf-8')
    full_answer = questions.get(question)

    update.message.reply_text(full_answer)

    return handle_new_question_request(bot, update)


def cancel(bot, update):
    """Хендлер заглушка для отмены диалога."""
    update.message.reply_text('Спасибо за участие в викторине.')

    return ConversationHandler.END


def start_telegram_bot():
    """Основная функция."""

    quiz_telegram_bot_token = os.getenv('QUIZ_TELEGRAM_BOT_TOKEN')
    updater = Updater(token=quiz_telegram_bot_token)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            State.QUESTION: [RegexHandler(f'^({Button.QUESTION.value})$', handle_new_question_request)],

            State.ANSWER: [
                RegexHandler(f'^({Button.GIVE_UP.value})$', handle_give_up),
                RegexHandler(f'^({Button.QUESTION.value})$', handle_new_question_request),
                MessageHandler(Filters.text, handle_solution_attempt)
            ],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()


if __name__ == '__main__':
    questions = get_questions()

    r = get_redis_connect()

    start_telegram_bot()
