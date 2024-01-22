import random
import re

import settings


def extract_information(text, rules):
    """
    Извлекает информацию из текста с использованием правил.

    Параметры:
    - text (str): Исходный текст, из которого нужно извлечь информацию.
    - rules (list): Список правил для извлечения информации.
                   Каждое правило представлено в виде кортежа (название, регулярное выражение).

    Возвращает:
    - dict: Словарь, в котором ключи - это названия правил,
            а значения - это извлеченные из текста соответствующие фрагменты.
    """

    extracted_info = {}

    for rule_name, regex_pattern in rules:
        matches = re.findall(regex_pattern, text)

        if matches:
            extracted_info[rule_name] = matches

    return extracted_info

# Пример использования:

text_to_process = """
KitagawaMarin , Спонсор раздачи ЛУЧШИЙ магазин прокси zelenka.guru/threads/3771847/ ------------ ТВОЯ ПРОКСИ: 138.124.103.108 :64036:n8KzbjHt:yxukCh8d
"""

# Правила для извлечения номеров телефонов и электронных адресов
extraction_rules = [
    ('proxy_info', r'(\d+\.\d+\.\d+\.\d+) :(\d+):(\w+):(\w+)')
]

result = extract_information(text_to_process, extraction_rules)

# Извлекаем информацию
if 'proxy_info' in result:
    ip, port, login, password = result['proxy_info'][0]
    print(f"ip={ip}\nport={port}\nlogin={login}\npassword={password}")

# Выводим результат
print(result)



def convert_row_to_dict(row):
    fields = settings.DB_USERFIELDS
    return {field[0]: value for field, value in zip(fields, row)}


def random_number_in_range(input_string):
    # Разделение строки на два значения по пробелу
    min_value, max_value = map(int, input_string.split())

    # Генерация случайного числа в указанном диапазоне
    result = random.randint(min_value, max_value)

    return result