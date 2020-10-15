import os
import random
import logging
from enum import Enum

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler

from redis_handlers import get_redis_connect
from utils import Button, get_questions
from log_handlers import LogsToTelegramHandler

logger = logging.getLogger(__name__)


class State(Enum):
    QUESTION = 1
    ANSWER = 2
    GIVE_UP = 3


def start(bot, update):
    """Отправка сообщения на комманду /start."""
    custom_keyboard = [[Button.QUESTION.value, Button.GIVE_UP.value], [Button.MY_SCORE.value]]

    reply_markup = ReplyKeyboardMarkup(custom_keyboard)

    update.message.reply_text('Привет!', reply_markup=reply_markup)

    return State.QUESTION


def handle_new_question_request(bot, update, user_data):
    """Обрабатываем запрос на отправку нового вопроса."""
    user_id = f'tg-{update.effective_user.id}'
    message = random.choice(list(questions))
    r.set(user_id, message)
    update.message.reply_text(message)

    if 'question' in user_data:
        user_data['question'] += 1
    else:
        user_data['question'] = 1

    return State.ANSWER


def handle_solution_attempt(bot, update, user_data):
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
        if 'answer' in user_data:
            user_data['answer'] += 1
        else:
            user_data['answer'] = 1
    else:
        message = "Неправильно... Попробуешь ещё раз?"
        state = State.ANSWER

    update.message.reply_text(message)

    return state


def handle_give_up(bot, update, user_data):
    """Кнопка сдаться. Печатаем ответ на вопрос и присылаем следующий вопрос."""
    user_id = f'tg-{update.effective_user.id}'

    question = r.get(user_id)
    question = question.decode('utf-8')
    full_answer = questions.get(question)

    update.message.reply_text(f'Ответ: {full_answer}')

    return handle_new_question_request(bot, update, user_data)


def handle_my_score_request(bot, update, user_data):
    """Кнопка Мой счет. Печатаем количество заданных вопросов и правильных ответов."""

    message = f'Задано вопросов: {user_data.get("question", 0)}, верных ответов: {user_data.get("answer", 0)}.'

    update.message.reply_text(message)
    return State.ANSWER


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
            State.QUESTION: [
                RegexHandler(f'^({Button.QUESTION.value})$', handle_new_question_request, pass_user_data=True)
            ],

            State.ANSWER: [
                RegexHandler(f'^({Button.GIVE_UP.value})$', handle_give_up, pass_user_data=True),
                RegexHandler(f'^({Button.QUESTION.value})$', handle_new_question_request, pass_user_data=True),
                RegexHandler(f'^({Button.MY_SCORE.value})$', handle_my_score_request, pass_user_data=True),
                MessageHandler(Filters.text, handle_solution_attempt, pass_user_data=True)
            ],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()


if __name__ == '__main__':
    notification_telegram_token = os.getenv("NOTIFICATION_TELEGRAM_TOKEN")
    notification_chat_id = os.getenv("NOTIFICATION_TELEGRAM_CHAT_ID")
    logger.setLevel(logging.INFO)
    logger.addHandler(LogsToTelegramHandler(notification_telegram_token, notification_chat_id))

    logger.info('Telegram support bot started.')

    questions = get_questions()

    r = get_redis_connect()

    start_telegram_bot()
