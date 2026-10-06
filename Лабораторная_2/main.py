"""Шесть задач на регулярные выражения; запуск выводит примеры."""
import re
from datetime import date, datetime
from ipaddress import IPv4Address


def validate_login(login):
    """Латинская буква в начале, длина 5–20, в конце буква или цифра."""
    return re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{3,18}[A-Za-z0-9]', login) is not None


def find_dates(text):
    """Найти существующие даты с одинаковым разделителем.

    Двузначный год интерпретируется как 2000–2099; возвращается исходная запись.
    """
    pattern = r'(?<![\w./-])(\d{1,2})([./-])(\d{1,2})\2(\d{4}|\d{2})(?!\w|[./-]\d)'
    result = []
    for match in re.finditer(pattern, text, flags=re.ASCII):
        day, _, month, year = match.groups()
        try:
            date(int(year) + (2000 if len(year) == 2 else 0), int(month), int(day))
        except ValueError:
            continue
        result.append(match.group())
    return result


def parse_log(line):
    """Разобрать запись лога; при неверном формате вернуть ValueError.

    IP берётся из входа: несовпадение IP в примере задания является опечаткой.
    """
    pattern = (r'(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) '
               r'(?:DEBUG|INFO|WARNING|ERROR|CRITICAL) user=(?P<user>[A-Za-z0-9_]+) '
               r'action=(?P<action>[A-Za-z0-9_-]+) ip=(?P<ip>(?:\d{1,3}\.){3}\d{1,3})')
    match = re.fullmatch(pattern, line, flags=re.ASCII)
    if not match:
        raise ValueError('Неверный формат записи лога.')
    result = match.groupdict()
    datetime.strptime(result['date']+' '+result['time'], '%Y-%m-%d %H:%M:%S')
    IPv4Address(result['ip'])
    return result


def validate_password(password):
    """Проверить длину, буквы двух регистров, цифру и один из !@#$%^&*."""
    return re.fullmatch(r'(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*])[^\s]{8,}', password) is not None


def validate_email(email, domains):
    """Проверить обычный ASCII email и точное совпадение разрешённого домена.

    Поддерживается распространённая dot-atom запись без кавычек и IDN.
    """
    if len(email) > 254:
        return False
    pattern = r"(?P<local>[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*)@(?P<domain>[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+)"
    match = re.fullmatch(pattern, email)
    return bool(match and len(match['local']) <= 64 and match['domain'].lower() in {d.lower() for d in domains})


def normalize_phone(phone):
    """Преобразовать российский номер 8…/7…/+7… в +7XXXXXXXXXX.

    Разрешены пробелы, дефисы и одна пара скобок вокруг кода оператора.
    """
    if not re.fullmatch(r'\s*(?:\+7|7|8)[ -]*(?:\([0-9]{3}\)|[0-9]{3})[ -]*[0-9]{3}[ -]*[0-9]{2}[ -]*[0-9]{2}\s*', phone):
        raise ValueError('Ожидается российский номер из 11 цифр с префиксом 7 или 8.')
    digits = re.sub(r'[^0-9]', '', phone)
    return '+7' + digits[1:]


def main():
    """Показать воспроизводимые примеры всех шести функций."""
    print('Логин student_1:', validate_login('student_1'))
    print('Даты:', find_dates('Встречи 1.2.26, 29/02/2024 и ошибочная 31-02-2025.'))
    print('Лог:', parse_log('2024-02-10 14:23:01 INFO user=ada action=login ip=192.168.1.15'))
    print('Пароль:', validate_password('Study!2026'))
    print('Email:', validate_email('student@edu.ru', ['gmail.com', 'yandex.ru', 'edu.ru']))
    print('Телефон:', normalize_phone('8 (999) 123-45-67'))

if __name__ == '__main__':
    main()
