import re
from enum import Enum


class Button(Enum):
    QUESTION = 'Новый вопрос'
    GIVE_UP = 'Сдаться'
    MY_SCORE = 'Мой счет'


def get_questions_from_koi8r_file():
    """Открываем файл (в кодировке KOI8-R) с вопросами и возвращаем словарь вопрос: ответ."""
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
