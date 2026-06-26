"""Лабораторная 2. Валидация данных с помощью регулярных выражений."""

from __future__ import annotations

import re


def validate_login(login: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z](?:[A-Za-z0-9_]{3,18}[A-Za-z0-9])", login))


def find_dates(text: str) -> list[str]:
    pattern = r"\b(?:0?[1-9]|[12]\d|3[01])([./-])(?:0?[1-9]|1[0-2])\1(?:\d{2}|\d{4})\b"
    return [match.group(0) for match in re.finditer(pattern, text)]


def parse_log(line: str) -> dict[str, str]:
    pattern = (
        r"^(?P<date>\d{4}-\d{2}-\d{2})\s+"
        r"(?P<time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<level>INFO|WARNING|ERROR|DEBUG)\s+"
        r"user=(?P<user>[A-Za-z0-9_]+)\s+"
        r"action=(?P<action>[A-Za-z_]+)\s+"
        r"ip=(?P<ip>(?:\d{1,3}\.){3}\d{1,3})$"
    )
    match = re.fullmatch(pattern, line)
    if not match:
        raise ValueError("Строка лога не соответствует формату")
    data = match.groupdict()
    octets = [int(part) for part in data["ip"].split(".")]
    if any(part > 255 for part in octets):
        raise ValueError("Некорректный IP-адрес")
    return data


def validate_password(password: str) -> bool:
    checks = [
        len(password) >= 8,
        re.search(r"[A-Z]", password),
        re.search(r"[a-z]", password),
        re.search(r"\d", password),
        re.search(r"[!@#$%^&*]", password),
    ]
    return all(checks)


def validate_email(email: str, domains: list[str]) -> bool:
    domain_pattern = "|".join(re.escape(domain) for domain in domains)
    pattern = rf"^[A-Za-z0-9._%+-]+@(?:{domain_pattern})$"
    return bool(re.fullmatch(pattern, email))


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 11 and digits[0] in {"7", "8"}:
        return "+7" + digits[1:]
    if len(digits) == 10:
        return "+7" + digits
    raise ValueError("Номер должен содержать 10 цифр или российский код 7/8")


def demo():
    print("Логин user_1:", validate_login("user_1"))
    print("Логин 1_user:", validate_login("1_user"))
    print("Даты:", find_dates("Встречи: 1.02.2024, 10-03-24 и 31/12/2025."))
    print("Лог:", parse_log("2024-02-10 14:23:01 INFO user=ada action=login ip=192.168.1.15"))
    print("Пароль:", validate_password("Strong!123"))
    print("Email:", validate_email("student@edu.ru", ["gmail.com", "yandex.ru", "edu.ru"]))
    print("Телефон:", normalize_phone("8 (999) 123-45-67"))


if __name__ == "__main__":
    demo()
