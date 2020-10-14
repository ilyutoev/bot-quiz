import re


with open('questions.txt', 'r', encoding='KOI8-R') as f:
    a = f.read()

questions = {}
question = ''
for line in a.split('\n\n'):
    if 'Вопрос' in line:
        question = re.sub(r'Вопрос .+:?\n', '', line).replace('\n', ' ').strip()
    if 'Ответ' in line:
        answer = line.replace('Ответ:', '').replace('\n', ' ').strip()
        questions[question] = answer
