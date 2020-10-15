import os
import random
import logging

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from redis_handlers import get_redis_connect
from utils import Button, get_questions
from log_handlers import LogsToTelegramHandler

logger = logging.getLogger(__name__)


def get_keyboard():
    """Настраиваем и возвращаем кнопки для чата."""
    keyboard = VkKeyboard()

    keyboard.add_button(Button.QUESTION.value, color=VkKeyboardColor.POSITIVE)
    keyboard.add_button(Button.GIVE_UP.value, color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button(Button.MY_SCORE.value, color=VkKeyboardColor.SECONDARY)

    return keyboard


def handle_new_question_request(event, vk_api):
    """Обрабатываем запрос на отправку нового вопроса."""
    keyboard = get_keyboard()

    user_id = f'vk-{event.user_id}'
    message = random.choice(list(questions))
    r.set(user_id, message)
    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )

    r.incr(f'{user_id}-questions', amount=1)


def handle_give_up(event, vk_api):
    """Кнопка сдаться. Печатаем ответ на вопрос и присылаем следующий вопрос."""
    keyboard = get_keyboard()

    user_id = f'vk-{event.user_id}'

    question = r.get(user_id)
    question = question.decode('utf-8')
    full_answer = questions.get(question)

    vk_api.messages.send(
        user_id=event.user_id,
        message=f'Ответ: {full_answer}',
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )

    handle_new_question_request(event, vk_api)


def handle_solution_attempt(event, vk_api):
    """Обработка ответа на вопрос."""

    keyboard = get_keyboard()
    user_id = f'vk-{event.user_id}'
    user_message = event.text

    question = r.get(user_id)
    question = question.decode('utf-8')
    full_answer = questions.get(question)
    short_answer = full_answer.split('.')[0].split('(')[0]

    if user_message.lower() == short_answer.lower():
        message = "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
        r.incr(f'{user_id}-answer', amount=1)
    else:
        message = "Неправильно... Попробуешь ещё раз?"

    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )


def handle_my_score_request(event, vk_api):
    """Кнопка Мой счет. Печатаем количество заданных вопросов и правильных ответов."""
    keyboard = get_keyboard()
    user_id = f'vk-{event.user_id}'

    questions_num = r.get(f'{user_id}-questions').decode('utf-8') if r.get(f'{user_id}-questions') else 0
    answers_num = r.get(f'{user_id}-answer').decode('utf-8') if r.get(f'{user_id}-answer') else 0

    message = f"Задано вопросов: {questions_num}, верных ответов: {answers_num}."

    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )


if __name__ == "__main__":
    notification_telegram_token = os.getenv("NOTIFICATION_TELEGRAM_TOKEN")
    notification_chat_id = os.getenv("NOTIFICATION_TELEGRAM_CHAT_ID")
    logger.setLevel(logging.INFO)
    logger.addHandler(LogsToTelegramHandler(notification_telegram_token, notification_chat_id))

    logger.info('VKontkte support bot started.')

    questions = get_questions()

    r = get_redis_connect()

    vk_token = os.getenv('QUIZ_VK_TOKEN')
    vk_session = vk_api.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == Button.QUESTION.value:
                handle_new_question_request(event, vk_api)
            elif event.text == Button.GIVE_UP.value:
                handle_give_up(event, vk_api)
            elif event.text == Button.MY_SCORE.value:
                handle_my_score_request(event, vk_api)
            else:
                handle_solution_attempt(event, vk_api)
